"""Audit fixed artifacts, configuration isolation, actual traces and rate limit."""

from collections import Counter
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))

from src import config
from src.chunking import build_chunks
from src.corpus import load_corpus
from src.eval_runner import eval_set_sha256, load_eval_set


def read(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def traces(label):
    return [json.loads(line) for line in (HERE / (label + "-answers.jsonl")).read_text(encoding="utf-8").splitlines()]


def main(output):
    start = read("baseline-manifest.json")
    allowed = {"src/config.py", "src/retrieval.py", "src/cli.py", "tests/conftest.py", ".env.example", "README.md"}
    changed = [name for name, digest in start["tracked_sha256"].items()
               if not (ROOT / name).is_file() or hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest]
    assert set(changed) <= allowed, changed
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip() == start["commit"]
    assert not subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT).strip()
    assert config.TOP_K == 3 and config.STOPWORDS_ENABLED is True and config.CURRENT_ONLY is True
    assert config.RETRIEVAL_MIN_SCORE == 0.01 and config.REFUSAL_THRESHOLD == 0.10
    assert config.RETRIEVAL_BACKEND == "lexical"
    sha = eval_set_sha256()
    questions = load_eval_set()
    by_id = {chunk.chunk_id: chunk for chunk in build_chunks(load_corpus())}
    base_config = read("lexical-extractive-before.json")["config"]
    metadata = {"RETRIEVAL_BACKEND", "EMBEDDING_MODEL", "EMBEDDING_REVISION", "EMBEDDING_DEVICE", "EMBEDDING_CACHE_DIR"}
    summaries = {}
    completed = ["lexical-extractive-before", "lexical-extractive-after", "semantic-extractive-after",
                 "lexical-gemma-before", "lexical-gemma-control"]
    for label in completed:
        result = read(label + ".json")
        actual = traces(label)
        assert result["eval_set_sha256"] == sha
        assert len(actual) == len(result["results"]) == len(questions) == 12
        assert [row["id"] for row in result["results"]] == [q["id"] for q in questions]
        for question, row, trace in zip(questions, result["results"], actual, strict=True):
            assert trace["question"] == question["question"]
            assert trace["status"] in {"complete", "local_refusal"}
            assert row["got"] == ("refuse" if trace["refused"] else "answer")
            assert row["cited_chunk_ids"] == trace["citations"]
            assert [r["chunk_id"] for r in row["top_k"]] == [r["chunk_id"] for r in trace["retrieved"]]
            assert [r["score"] for r in row["top_k"]] == [round(r["score"], 6) for r in trace["retrieved"]]
            assert all(by_id[r["chunk_id"]].status != "superseded" for r in trace["retrieved"])
        settings = result["config"]
        assert {k: v for k, v in settings.items() if k not in metadata | {"ANSWER_BACKEND"}} == {
            k: v for k, v in base_config.items() if k != "ANSWER_BACKEND"}
        summaries[label] = result["summary"]
    for before, after in [("lexical-extractive-before", "lexical-extractive-after"),
                          ("lexical-gemma-before", "lexical-gemma-control")]:
        assert read(before + ".json")["results"] == read(after + ".json")["results"]
        assert read(before + ".json")["summary"] == read(after + ".json")["summary"]
    lexical = read("lexical-extractive-after.json")["config"]
    semantic = read("semantic-extractive-after.json")["config"]
    assert {key for key in lexical if lexical[key] != semantic[key]} == {"RETRIEVAL_BACKEND"}
    interrupted = {}
    for label in ["semantic-gemma-after", "semantic-gemma-recovery"]:
        assert not (HERE / (label + ".json")).exists()
        rows = traces(label)
        assert len(rows) == 9 and rows[-1]["question"] == questions[8]["question"]
        assert rows[-1]["status"] == "error" and rows[-1]["error_type"] == "InvalidResponseError"
        assert [r["question"] for r in rows] == [q["question"] for q in questions[:len(rows)]]
        e05 = rows[4]
        assert not e05["refused"] and "5 business days" in e05["answer"]
        assert e05["citations"] == ["hb-01-chunk-1"]
        interrupted[label] = {"questions_traced": len(rows), "last_error": rows[-1]["error"]}
    for label in ["semantic-e05-cli", "semantic-e10-cli", "semantic-e11-cli", "semantic-e12-cli"]:
        row = traces(label)[0]
        assert row["status"] != "error"
        if "e05" in label:
            assert not row["refused"] and "5 business days" in row["answer"]
        else:
            assert row["refused"] and not row["citations"]
    assert traces("semantic-e09-cli")[0]["error_type"] == "InvalidResponseError"
    diagnostic = read("e09-raw-decision.json")
    assert diagnostic["accepted"] is False
    raw = json.loads(diagnostic["raw_decision"])
    assert raw["citations"] == ["hb-01-chunk-1", "hb-01-chunk-2"]
    assert "[hb-01-chunk-1, hb-01-chunk-2]" in raw["answer"]
    starts = [json.loads(line) for line in (HERE / "request-starts.jsonl").read_text().splitlines()]
    times = [row["monotonic"] for row in starts]
    gap = min(b - a for a, b in zip(times, times[1:]))
    peak = max(sum(0 <= other - start < 60 for other in times) for start in times)
    assert gap >= 2.1 - 0.001 and peak <= 30
    model = read("real-model-verification.json")
    assert model["dimension"] == 384 and model["all_chunks_fit_model"]
    assert model["encoding_batch_sizes"] == [24, 1, 1]
    all_traces = [row for path in HERE.glob("*-answers.jsonl") for row in traces(path.name[:-14])]
    total_usage = sum(row["usage"].get("totalTokenCount", 0) for row in all_traces)
    attempt_statuses = dict(Counter(attempt["status"] for row in all_traces for attempt in row["attempts"]))
    assert sum(len(row["attempts"]) for row in all_traces) == len(starts)
    key = os.environ.get("GEMINI_API_KEY", "")
    if key:
        for directory in [HERE, ROOT / "specs/007-semantic-retrieval"]:
            for path in directory.rglob("*"):
                if path.is_file() and "_pytest" not in path.parts and path.suffix in {".json", ".jsonl", ".md", ".txt", ".py", ".diff"}:
                    assert key not in path.read_text(encoding="utf-8"), path.name
    documents = [ROOT / "README.md", ROOT / "docs/semantic-retrieval-report.md",
                 *(ROOT / "specs/007-semantic-retrieval").rglob("*.md")]
    missing = [(str(path.relative_to(ROOT)), target) for path in documents
               for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8"))
               if "://" not in target and not (path.parent / target.split("#")[0]).exists()
               and not (path.parent / target).resolve() == (HERE / output).resolve()]
    assert not missing, missing
    assert (HERE / "implementation.diff").is_file()
    result = {"checks_passed": True, "original_commit": start["commit"],
        "protected_existing_files": len(start["tracked_sha256"]), "changed_existing_files": changed,
        "eval_set_sha256": sha, "all_existing_config_values_preserved": True,
        "only_backend_differs_in_same_snapshot_control": True,
        "lexical_result_rows_reproduced_exactly": True,
        "complete_evaluations": summaries, "interrupted_evaluations": interrupted,
        "e05_live_answer_verified": True, "unsupported_live_cli_refusals_verified": True,
        "e09_combined_inline_citation_diagnosed": True,
        "request_attempts": len(starts), "minimum_request_gap_seconds": gap,
        "peak_requests_in_rolling_minute": peak, "user_limit_per_minute": 30,
        "requested_models": dict(Counter(row["model"] for row in starts)),
        "attempt_statuses": attempt_statuses,
        "fallback_records": sum(row["fallback_used"] for row in all_traces),
        "local_document_links_valid": True, "implementation_diff_saved": True,
        "reported_total_tokens": total_usage, "credential_scan_performed": bool(key),
        "work_uncommitted_and_unstaged": True}
    if Path(output).name != output:
        raise ValueError("Use an evidence filename without directories.")
    with (HERE / output).open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="verification.json")
    main(parser.parse_args().output)
