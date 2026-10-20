"""Reproduce this config experiment without changing application files.

Run from repository root with .venv/Scripts/python.exe. Each measurement runs
the existing module entry point in a fresh process. Outputs are never replaced.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MODES = {"before": (2, False), "topk-only": (3, False),
         "stopwords-only": (2, True), "after": (3, True)}
PREFIX = {"extractive": "extractive", "gemma": "gemma-live"}
# Pin only these settings in child process memory; then use the original entry
# point, including its argument parsing, output writing and metric calculations.
BOOTSTRAP = """
import json, os, runpy, sys, time
from datetime import datetime, timezone
from pathlib import Path
from src import config
module, top_k, stopwords = sys.argv[1:4]
config.TOP_K = int(top_k)
config.STOPWORDS_ENABLED = stopwords == 'True'
if config.ANSWER_BACKEND == 'gemma':
    from src import gemma_client
    original_open = gemma_client._open
    state = Path(os.environ['CONFIG_VERIFICATION_RATE_STATE'])
    requests = state.with_name('rate-limit-requests.jsonl')
    def paced_open(request, timeout):
        # All subprocesses run sequentially and share one monotonic clock/state.
        # Space every transport attempt, including retries and fallback, by 2.1s.
        previous = float(state.read_text()) if state.exists() else 0.0
        time.sleep(max(0.0, 2.1 - (time.monotonic() - previous)))
        started = time.monotonic()
        state.write_text(str(started))
        with requests.open('a', encoding='utf-8') as stream:
            stream.write(json.dumps({'started_monotonic': started,
                'started_utc': datetime.now(timezone.utc).isoformat(),
                'model': request.full_url.split('/models/', 1)[1].split(':', 1)[0]}) + '\\n')
        return original_open(request, timeout=timeout)
    gemma_client._open = paced_open
sys.argv = [module] + sys.argv[4:]
runpy.run_module(module, run_name='__main__')
"""


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def save_json(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def capture(name, command, *, backend=None, trace=None):
    if not re.fullmatch(r"[a-z0-9-]+", name):
        raise ValueError("Evidence labels must be simple lowercase names.")
    destination = HERE / f"{name}.txt"
    if destination.exists():
        raise FileExistsError(f"Preserve existing evidence: {destination.name}")
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env.pop("GEMMA_TRACE_PATH", None)
    if backend is not None:
        env["ANSWER_BACKEND"] = backend
    if backend == "gemma":
        env["CONFIG_VERIFICATION_RATE_STATE"] = str(HERE / "_rate-limit.txt")
    if trace is not None:
        if trace.exists():
            raise FileExistsError(f"Preserve existing trace: {trace.name}")
        env["GEMMA_TRACE_PATH"] = str(trace)
    print(f"Running {name}", flush=True)
    started = datetime.now(timezone.utc)
    result = subprocess.run(command, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, encoding="utf-8", errors="replace")
    with destination.open("x", encoding="utf-8") as stream:
        stream.write(result.stdout)
    save_json(HERE / f"{name}-execution.json", {
        "command": command, "cwd": str(ROOT), "backend": backend,
        "trace": str(trace.relative_to(ROOT)) if trace else None,
        "started_utc": started.isoformat(),
        "ended_utc": datetime.now(timezone.utc).isoformat(),
        "returncode": result.returncode,
    })
    print(result.stdout[-3500:], flush=True)
    print(f"Exit: {result.returncode}; saved {destination.name}", flush=True)
    return result.returncode


def module_command(module, mode, *args):
    top_k, stopwords = MODES[mode]
    return [sys.executable, "-c", BOOTSTRAP, module, str(top_k), str(stopwords), *args]


def completed_label(backend, mode):
    original = f"{PREFIX[backend]}-{mode}"
    # An interrupted execution has no result JSON. Allow one explicit recovery
    # execution, keeping the original console, error trace and exit record.
    candidates = [name for name in (original, original + "-recovery")
                  if (HERE / f"{name}.json").exists()]
    if len(candidates) > 1:
        raise ValueError("Multiple completed runs must not be selected by score.")
    return candidates[0] if candidates else original


def initialise():
    tracked = git("ls-files", "-z").decode().split("\0")
    save_json(HERE / "starting-manifest.json", {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "local_date": "2026-10-21", "timezone": "Europe/Belgrade",
        "commit": git("rev-parse", "HEAD").decode().strip(),
        "parent": git("rev-parse", "HEAD^").decode().strip(),
        "branch": git("branch", "--show-current").decode().strip(),
        "python": platform.python_version(), "python_executable": sys.executable,
        "tracked_sha256": {name: digest(ROOT / name) for name in tracked
                           if name and (ROOT / name).is_file()},
        "user_run_sha256": digest(ROOT / "results/manualLLM.json"),
    })
    with (HERE / "parent-config.py.txt").open("xb") as stream:
        stream.write(git("show", "HEAD^:src/config.py"))
    with (HERE / "user-manualLLM.json").open("xb") as stream:
        stream.write((ROOT / "results/manualLLM.json").read_bytes())
    print("Saved starting identity, protected hashes, parent config and unchanged user run.")


def matrix(backend):
    failed = []
    for mode in MODES:
        label = completed_label(backend, mode)
        out = HERE / f"{label}.json"
        if out.exists():
            print(f"Preserving completed measurement {out.name}", flush=True)
            continue
        if (HERE / f"{label}.txt").exists():
            label += "-recovery"
            out = HERE / f"{label}.json"
            if (HERE / f"{label}.txt").exists():
                print(f"Preserving both interrupted attempts for {mode}; no score available.", flush=True)
                failed.append(mode)
                continue
        # The retained combination also exercises the ordinary documented command.
        command = ([sys.executable, "-m", "src.eval_runner", "--out", str(out)]
                   if mode == "after" and backend == "extractive"
                   else module_command("src.eval_runner", mode, "--out", str(out)))
        code = capture(label, command, backend=backend, trace=HERE / f"{label}-answers.jsonl")
        if code:
            failed.append(mode)
    return 1 if failed else 0


def comparisons(backend):
    for first, second in [("before", "after"), ("before", "topk-only"),
                          ("before", "stopwords-only"), ("stopwords-only", "after"),
                          ("topk-only", "after")]:
        name = f"{PREFIX[backend]}-compare-{first}-to-{second}"
        before = HERE / f"{completed_label(backend, first)}.json"
        after = HERE / f"{completed_label(backend, second)}.json"
        if not before.exists() or not after.exists():
            message = ("UNAVAILABLE: no complete evaluation result exists for one configuration. "
                       "Its interrupted execution is preserved; no score or comparison is inferred.\n")
            with (HERE / f"{name}.txt").open("x", encoding="utf-8") as stream:
                stream.write(message)
            print(name + ": " + message, flush=True)
            continue
        code = capture(name, [sys.executable, "-m", "src.eval_compare", str(before), str(after)])
        if code:
            return code
    return 0


def audit(offline_only=False):
    from src.chunking import build_chunks
    from src.corpus import load_corpus
    from src.eval_runner import eval_set_sha256, load_eval_set

    start = json.loads((HERE / "starting-manifest.json").read_text(encoding="utf-8"))
    allowed = {"src/config.py", "tests/test_generation_config.py", "README.md"}
    changed = [name for name, sha in start["tracked_sha256"].items()
               if not (ROOT / name).is_file() or digest(ROOT / name) != sha]
    assert set(changed) <= allowed, changed
    assert digest(ROOT / "results/manualLLM.json") == start["user_run_sha256"]
    assert digest(HERE / "user-manualLLM.json") == start["user_run_sha256"]
    questions = load_eval_set()
    chunks = {chunk.chunk_id: chunk for chunk in build_chunks(load_corpus())}
    current_sha = eval_set_sha256()
    runs = {}
    unavailable = {}
    for backend in (("extractive",) if offline_only else ("extractive", "gemma")):
        for mode, (top_k, stopwords) in MODES.items():
            label = completed_label(backend, mode)
            if not (HERE / f"{label}.json").exists():
                attempts = []
                for candidate in (label, label + "-recovery"):
                    execution_path = HERE / f"{candidate}-execution.json"
                    if not execution_path.exists():
                        continue
                    execution = json.loads(execution_path.read_text(encoding="utf-8"))
                    assert execution["returncode"] != 0
                    rows = [json.loads(line) for line in
                            (HERE / f"{candidate}-answers.jsonl").read_text(encoding="utf-8").splitlines()]
                    assert rows and rows[-1]["status"] == "error"
                    assert [r["question"] for r in rows] == [q["question"] for q in questions[:len(rows)]]
                    assert not (HERE / f"{candidate}.json").exists()
                    attempts.append({"label": candidate, "traced_questions": len(rows),
                                     "error_type": rows[-1]["error_type"], "error": rows[-1]["error"]})
                assert attempts, (backend, mode)
                unavailable[label] = attempts
                continue
            value = json.loads((HERE / f"{label}.json").read_text(encoding="utf-8"))
            traces = [json.loads(line) for line in (HERE / f"{label}-answers.jsonl").read_text(encoding="utf-8").splitlines()]
            assert value["eval_set_sha256"] == current_sha
            assert [row["id"] for row in value["results"]] == [q["id"] for q in questions]
            assert value["config"]["TOP_K"] == top_k
            assert value["config"]["STOPWORDS_ENABLED"] is stopwords
            assert value["config"]["ANSWER_BACKEND"] == backend
            assert len(traces) == len(questions)
            for question, row, trace in zip(questions, value["results"], traces, strict=True):
                assert trace["question"] == question["question"]
                assert trace["status"] != "error"
                assert trace["refused"] is (row["got"] == "refuse")
                assert trace["citations"] == row["cited_chunk_ids"]
                assert len(trace["retrieved"]) <= top_k
                assert all(chunks[r["chunk_id"]].status != "superseded" for r in trace["retrieved"])
                assert all(c in {r["chunk_id"] for r in trace["retrieved"]} for c in trace["citations"])
            runs[label] = value["summary"]
        reference = json.loads((HERE / f"{completed_label(backend, 'before')}.json").read_text(encoding="utf-8"))["config"]
        for mode, (top_k, stopwords) in MODES.items():
            if not (HERE / f"{completed_label(backend, mode)}.json").exists():
                continue
            actual = json.loads((HERE / f"{completed_label(backend, mode)}.json").read_text(encoding="utf-8"))["config"]
            expected = {**reference, "TOP_K": top_k, "STOPWORDS_ENABLED": stopwords}
            assert actual == expected, (backend, mode)
    # Answers and attempts can include user-supplied strings: verify saved artifacts
    # contain no accidental copy of the actual locally loaded credential.
    key = os.environ.get("GEMINI_API_KEY", "")
    if key:
        for path in HERE.rglob("*"):
            if path.is_file() and path.suffix in {".json", ".jsonl", ".txt", ".md", ".py"}:
                assert key not in path.read_text(encoding="utf-8"), path.name
    user = json.loads((HERE / "user-manualLLM.json").read_text(encoding="utf-8"))
    retained = json.loads((HERE / "extractive-after.json").read_text(encoding="utf-8"))
    assert user["eval_set_sha256"] == current_sha
    assert [r["top_k"] for r in user["results"]] == [r["top_k"] for r in retained["results"]]
    pacing = None
    if not offline_only:
        starts = [json.loads(line)["started_monotonic"] for line in
                  (HERE / "rate-limit-requests.jsonl").read_text(encoding="utf-8").splitlines()]
        minimum_gap = min(b - a for a, b in zip(starts, starts[1:]))
        maximum_minute = max(sum(0 <= other - start < 60 for other in starts) for start in starts)
        assert minimum_gap >= 2.1 - 0.001
        assert maximum_minute <= 30
        pacing = {"attempts": len(starts), "minimum_gap_seconds": minimum_gap,
                  "maximum_attempts_in_rolling_minute": maximum_minute,
                  "user_limit_per_minute": 30}
    save_json(HERE / ("offline-verification.json" if offline_only else "verification.json"), {
        "all_checks_passed": True, "eval_set_sha256": current_sha,
        "protected_tracked_files": len(start["tracked_sha256"]),
        "changed_existing_files": changed, "original_user_run_preserved": True,
        "complete_measurements_checked": len(runs),
        "operationally_interrupted_configurations": unavailable,
        "all_checked_runs_and_traces_aligned": True,
        "hosted_verification_pending": offline_only,
        "all_other_settings_identical_within_backend": True,
        "retained_retrieval_matches_original_user_run": True,
        "request_rate_check": pacing,
        "credential_scan_performed": bool(key), "summaries": runs,
    })
    print(json.dumps(runs, indent=2))
    print("Integrity and result/trace alignment checks passed.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["init", "pytest", "matrix", "compare", "cli", "audit"])
    parser.add_argument("--backend", choices=["extractive", "gemma"], default="gemma")
    parser.add_argument("--mode", choices=list(MODES), default="after")
    parser.add_argument("--label")
    parser.add_argument("--question")
    parser.add_argument("--offline-only", action="store_true")
    args = parser.parse_args()
    if args.action == "init":
        initialise()
    elif args.action == "pytest":
        label = args.label or f"pytest-{args.mode}"
        if not re.fullmatch(r"[a-z0-9-]+", label):
            parser.error("Use a simple lowercase evidence label.")
        temporary = HERE / "_pytest" / label
        if temporary.exists():
            raise FileExistsError("Use a fresh pytest label and temporary directory.")
        temporary.parent.mkdir(exist_ok=True)
        options = ["-p", "no:cacheprovider", "--basetemp", str(temporary)]
        command = ([sys.executable, "-m", "pytest", *options] if args.mode == "after"
                   else module_command("pytest", args.mode, *options))
        return capture(label, command, backend="extractive")
    elif args.action == "matrix":
        return matrix(args.backend)
    elif args.action == "compare":
        return comparisons(args.backend)
    elif args.action == "cli":
        if not args.label or not args.question:
            parser.error("cli requires --label and --question")
        command = (module_command("src.cli", "after", "--question", args.question, "--show-retrieved")
                   if args.backend == "gemma" else
                   [sys.executable, "-m", "src.cli", "--question", args.question, "--show-retrieved"])
        return capture(args.label, command, backend=args.backend,
            trace=HERE / f"{args.label}-answers.jsonl")
    elif args.action == "audit":
        audit(args.offline_only)
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    raise SystemExit(main())
