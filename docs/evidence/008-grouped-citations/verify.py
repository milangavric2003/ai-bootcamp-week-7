"""Check the citation-only follow-up, actual answers, controls and rate limit."""

from collections import Counter
import json
import os
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))

import checkpoint
from src import config
from src.chunking import build_chunks
from src.corpus import load_corpus
from src.eval_runner import eval_set_sha256, load_eval_set


def read(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def trace(label):
    return [json.loads(line) for line in (HERE / (label + "-answers.jsonl")).read_text(encoding="utf-8").splitlines()]


def main():
    manifest = read("before-manifest.json")
    current = checkpoint.hashes()
    changed = [name for name, sha in manifest["sha256"].items() if current.get(name) != sha]
    assert set(changed) <= {"src/generation.py", "tests/test_generation.py", "README.md", "docs/semantic-retrieval-report.md"}, changed
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip() == manifest["commit"]
    assert not subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT).strip()
    questions = load_eval_set()
    sha = eval_set_sha256()
    chunks = {chunk.chunk_id: chunk for chunk in build_chunks(load_corpus())}
    summaries = {}
    for label in ["semantic-extractive-before", "semantic-extractive-after", "semantic-gemma-after", "lexical-gemma-control"]:
        result, actual = read(label + ".json"), trace(label)
        assert result["eval_set_sha256"] == sha
        assert len(result["results"]) == len(actual) == len(questions) == 12
        for item, row, answer in zip(questions, result["results"], actual, strict=True):
            assert row["id"] == item["id"] and answer["question"] == item["question"]
            assert answer["status"] != "error"
            assert row["got"] == ("refuse" if answer["refused"] else "answer")
            assert row["cited_chunk_ids"] == answer["citations"]
            retrieved = {r["chunk_id"] for r in answer["retrieved"]}
            assert set(answer["citations"]) <= retrieved
            assert all(chunks[cid].status != "superseded" for cid in retrieved)
            if answer["backend"] == "gemma":
                assert all(marker in answer["citations"] for marker in re.findall(r"\[([^\[\]]*)\]", answer["answer"]))
            assert row["top_k"] == [{"chunk_id": r["chunk_id"], "score": round(r["score"], 6)} for r in answer["retrieved"]]
        summaries[label] = result["summary"]
    before = read("semantic-extractive-before.json")
    after = read("semantic-extractive-after.json")
    assert before["config"] == after["config"] and before["results"] == after["results"] and before["summary"] == after["summary"]
    semantic = read("semantic-gemma-after.json")
    lexical = read("lexical-gemma-control.json")
    assert {key for key in semantic["config"] if semantic["config"][key] != lexical["config"][key]} == {"RETRIEVAL_BACKEND"}
    assert {k: v for k, v in semantic["config"].items() if k != "ANSWER_BACKEND"} == {
        k: v for k, v in before["config"].items() if k != "ANSWER_BACKEND"}
    assert semantic["summary"]["passed"] == 12 and lexical["summary"]["passed"] == 11
    previous_lexical = json.loads((HERE.parent / "007-semantic-retrieval/lexical-gemma-control.json").read_text(encoding="utf-8"))
    assert lexical["results"] == previous_lexical["results"] and lexical["summary"] == previous_lexical["summary"]
    assert semantic["config"]["TOP_K"] == 3 and semantic["config"]["STOPWORDS_ENABLED"] is True
    assert semantic["config"]["RETRIEVAL_MIN_SCORE"] == 0.01 and semantic["config"]["REFUSAL_THRESHOLD"] == 0.1
    cli = trace("semantic-e09-cli")[0]
    assert not cli["refused"] and cli["status"] == "complete"
    assert "5 business days" in cli["answer"] and "manager approval" in cli["answer"]
    assert "IT portal under Hardware" in cli["answer"]
    assert set(cli["citations"]) == {"hb-01-chunk-1", "hb-01-chunk-2"}
    replay = read("captured-decision-replay.json")
    assert replay["before_error"] and not replay["after_refused"]
    assert replay["after_answer"].endswith("[hb-01-chunk-1] [hb-01-chunk-2].")
    starts = [json.loads(s) for s in (HERE / "request-starts.jsonl").read_text().splitlines()]
    times = [r["monotonic"] for r in starts]
    gap = min(b - a for a, b in zip(times, times[1:]))
    peak = max(sum(0 <= other - start < 60 for other in times) for start in times)
    assert gap >= 2.1 - 0.001 and peak <= 30
    rows = trace("semantic-gemma-after") + trace("lexical-gemma-control") + trace("semantic-e09-cli")
    fallback = [{"question": r["question"], "model": r["model"]} for r in trace("semantic-gemma-after") if r["fallback_used"]]
    assert len(starts) == sum(len(r["attempts"]) for r in rows)
    key = os.environ.get("GEMINI_API_KEY", "")
    scan = [*HERE.rglob("*"), * (ROOT / "specs/008-grouped-citations").rglob("*"), ROOT / "docs/grouped-citations-report.md"]
    if key:
        for path in scan:
            if path.is_file() and "_pytest" not in path.parts and path.suffix in {".py", ".md", ".txt", ".json", ".jsonl"}:
                assert key not in path.read_text(encoding="utf-8"), path.name
    for document in [ROOT / "README.md", ROOT / "docs/grouped-citations-report.md", ROOT / "docs/semantic-retrieval-report.md",
                     *(ROOT / "specs/008-grouped-citations").rglob("*.md")]:
        for target in re.findall(r"\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
            if "://" not in target:
                resolved = (document.parent / target.split("#")[0]).resolve()
                assert resolved.exists() or resolved == HERE / "verification.json", (document, target)
    patch = subprocess.check_output(["git", "--no-pager", "diff", "--no-ext-diff", "HEAD", "--",
                                    "src/generation.py", "tests/test_generation.py"], cwd=ROOT, timeout=15)
    with (HERE / "implementation.diff").open("xb") as stream:
        stream.write(patch)
    result = {"checks_passed": True, "protected_starting_files": len(manifest["sha256"]),
        "changed_existing_files": changed, "previous_embedding_implementation_and_evidence_preserved": True,
        "eval_set_sha256": sha, "existing_settings_and_prompt_preserved": True,
        "offline_result_rows_unchanged": True, "lexical_hosted_result_rows_unchanged": True,
        "summaries": summaries, "semantic_fallback_answers": fallback,
        "request_attempts": len(starts), "minimum_gap_seconds": gap,
        "peak_requests_per_rolling_minute": peak, "user_limit": 30,
        "request_models": dict(Counter(r["model"] for r in starts)),
        "attempt_statuses": dict(Counter(a["status"] for r in rows for a in r["attempts"])),
        "reported_total_tokens": sum(r["usage"].get("totalTokenCount", 0) for r in rows),
        "no_hybrid_or_threshold_change": True, "uncommitted_and_unstaged": True,
        "credential_scan_performed": bool(key), "local_document_links_valid": True}
    with (HERE / "verification.json").open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
