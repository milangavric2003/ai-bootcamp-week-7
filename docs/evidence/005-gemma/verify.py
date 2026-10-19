"""Verify saved offline equivalence and protected files; does not calculate metrics."""

import argparse
import hashlib
import json
from pathlib import Path


root = Path(__file__).resolve().parents[3]
evidence = Path(__file__).resolve().parent
before = json.loads((evidence / "original-before.json").read_text(encoding="utf-8"))
retained = json.loads((evidence / "retained-extractive.json").read_text(encoding="utf-8"))
manifest = json.loads((evidence / "before-manifest.json").read_text(encoding="utf-8"))

assert before["eval_set_sha256"] == retained["eval_set_sha256"]
assert before["results"] == retained["results"], "Per-question retrieval/behavior/metric rows changed"
assert before["summary"] == retained["summary"]
assert all(retained["config"][k] == v for k, v in before["config"].items())
assert retained["config"]["STOPWORDS_ENABLED"] is False
allowed_edits = {"src/config.py", "src/rag.py", "src/cli.py", "requirements.txt", ".gitignore"}
protected = {p: sha for p, sha in manifest["sha256"].items() if p not in allowed_edits}
for path, expected in protected.items():
    assert hashlib.sha256((root / path).read_bytes()).hexdigest() == expected, path

traces = [json.loads(line) for line in (evidence / "retained-answers.jsonl").read_text(encoding="utf-8").splitlines()]
assert len(traces) == len(retained["results"]) == 12
assert all(row["backend"] == "extractive" for row in traces)
assert all(row["status"] in ("complete", "local_refusal") for row in traces)
for trace, row in zip(traces, retained["results"]):
    assert trace["citations"] == row["cited_chunk_ids"]
    assert trace["refused"] == (row["got"] == "refuse")

template = (root / ".env.example").read_text(encoding="utf-8")
assert "\nGEMINI_API_KEY=\n" in template
output = json.dumps({"status": "passed", "questions": 12, "passed": retained["summary"]["passed"],
                  "protected_files_unchanged": len(protected), "eval_set_sha256": retained["eval_set_sha256"],
                  "same_per_question_results": True, "same_original_settings": True,
                  "same_run_answer_trace_records": len(traces)}, indent=2)
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--out", type=Path)
args = parser.parse_args()
if args.out:
    with args.out.open("x", encoding="utf-8") as stream:
        stream.write(output + "\n")
print(output)
