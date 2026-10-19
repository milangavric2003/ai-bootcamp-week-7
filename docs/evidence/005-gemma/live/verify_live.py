"""Audit saved live evidence and compare unchanged runner outputs; no inference."""

import hashlib
import json
from pathlib import Path
from statistics import mean, median
import sys

root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(root))
from src.eval_compare import compare_runs

folder = Path(__file__).resolve().parent
before = json.loads((folder / "before.json").read_text(encoding="utf-8"))
after = json.loads((folder / "after.json").read_text(encoding="utf-8"))
manifest = json.loads((folder / "run-manifest.json").read_text(encoding="utf-8"))
comparison = compare_runs(before, after)
assert comparison["changed_settings"] == {"ANSWER_BACKEND": ("extractive", "gemma")}
assert comparison["warning"] is None
assert len(before["results"]) == len(after["results"]) == 12
assert [r["id"] for r in before["results"]] == [r["id"] for r in after["results"]]
assert all(a["top_k"] == b["top_k"] for a, b in zip(before["results"], after["results"]))
for path, expected in manifest["sha256"].items():
    assert hashlib.sha256((root / path).read_bytes()).hexdigest() == expected, path

def traces(name):
    return [json.loads(line) for line in (folder / name).read_text(encoding="utf-8").splitlines()]

baseline_answers = traces("before-answers.jsonl")
answers = traces("after-answers.jsonl")
questions = json.loads((root / "eval/eval_set.json").read_text(encoding="utf-8"))
assert len(baseline_answers) == len(answers) == len(questions) == 12
for question, old, answer, row in zip(questions, baseline_answers, answers, after["results"]):
    assert question["question"] == old["question"] == answer["question"]
    assert old["retrieved"] == answer["retrieved"]
    assert answer["citations"] == row["cited_chunk_ids"]
    assert answer["refused"] == (row["got"] == "refuse")
    assert answer["status"] in ("complete", "local_refusal")
    assert answer["model"] == after["config"]["GEMMA_MODEL"]
    assert answer["prompt_sha256"] == after["config"]["GEMMA_PROMPT_SHA256"]
remote = [answer for answer in answers if answer["status"] == "complete"]
probe = traces("probe-01.jsonl")
cli = traces("E11-cli-answers.jsonl")
assert len(probe) == 2 and not probe[0]["refused"] and probe[1]["refused"]
assert "17:00" in probe[0]["answer"]
assert len(cli) == 1 and cli[0]["refused"] and not cli[0]["citations"]

usage_fields = ("promptTokenCount", "candidatesTokenCount", "totalTokenCount")
def usage(rows):
    return {field: sum(row["usage"].get(field, 0) for row in rows) for field in usage_fields}

report = {
    "status": "passed", "eval_set_sha256": after["eval_set_sha256"],
    "same_retrieval_for_all_questions": True, "runtime_matches_frozen_manifest": True,
    "changed_settings": comparison["changed_settings"], "comparison_warning": comparison["warning"],
    "before_summary": before["summary"], "after_summary": after["summary"],
    "fixed": comparison["fixed"], "regressed": comparison["regressed"],
    "same_run_answer_records": len(answers), "eval_remote_requests": len(remote),
    "eval_local_refusals": len(answers) - len(remote), "eval_usage": usage(remote),
    "eval_remote_latency_ms": {"min": min(row["elapsed_ms"] for row in remote),
                               "mean": round(mean(row["elapsed_ms"] for row in remote), 3),
                               "median": round(median(row["elapsed_ms"] for row in remote), 3),
                               "max": max(row["elapsed_ms"] for row in remote)},
    "successful_remote_requests_including_probe_and_cli": len(remote) + len(probe) + len(cli),
    "usage_including_probe_and_cli": usage(remote + probe + cli),
    "provider_billing_audited": False,
}
output = json.dumps(report, indent=2)
if "--out" in sys.argv:
    with (folder / "verification.json").open("x", encoding="utf-8") as stream:
        stream.write(output + "\n")
print(output)
