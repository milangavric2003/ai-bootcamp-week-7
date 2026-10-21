"""Run the semantic-retrieval experiment from repository root; never replace evidence."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PACED_MODULE = """
import json, os, runpy, sys, time
from datetime import datetime, timezone
from pathlib import Path
from src import gemma_client
original = gemma_client._open
state = Path(os.environ['EXPERIMENT_REQUEST_STATE'])
def paced(request, timeout):
    previous = float(state.read_text()) if state.exists() else 0.0
    time.sleep(max(0, 2.1 - (time.monotonic() - previous)))
    now = time.monotonic()
    state.write_text(str(now))
    with state.with_name('request-starts.jsonl').open('a', encoding='utf-8') as log:
        log.write(json.dumps({'monotonic': now, 'utc': datetime.now(timezone.utc).isoformat(),
            'model': request.full_url.split('/models/', 1)[1].split(':', 1)[0]}) + '\\n')
    return original(request, timeout=timeout)
gemma_client._open = paced
module = sys.argv.pop(1)
sys.argv[0] = module
if module.endswith('.py'):
    runpy.run_path(module, run_name='__main__')
else:
    runpy.run_module(module, run_name='__main__')
"""


def write_json(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write("\n")


def execute(label, command, *, backend="extractive", retrieval="lexical", trace=False, offline_model=True):
    if not label or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in label):
        raise ValueError("Use a simple lowercase evidence label.")
    out = HERE / (label + ".txt")
    if out.exists():
        raise FileExistsError(out.name)
    env = os.environ.copy()
    env.update(PYTHONIOENCODING="utf-8", ANSWER_BACKEND=backend,
               RAG_RETRIEVAL_BACKEND=retrieval, HF_HUB_OFFLINE="1",
               EXPERIMENT_REQUEST_STATE=str(HERE / "_last-request.txt"))
    env.pop("GEMMA_TRACE_PATH", None)
    if not offline_model:
        env.pop("HF_HUB_OFFLINE", None)
    if trace:
        destination = HERE / (label + "-answers.jsonl")
        if destination.exists():
            raise FileExistsError(destination.name)
        env["GEMMA_TRACE_PATH"] = str(destination)
    print("Running " + label, flush=True)
    started = datetime.now(timezone.utc).isoformat()
    result = subprocess.run(command, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, encoding="utf-8", errors="replace")
    with out.open("x", encoding="utf-8") as stream:
        stream.write(result.stdout)
    write_json(HERE / (label + "-execution.json"), {
        "command": command, "backend": backend, "retrieval": retrieval,
        "started_utc": started, "ended_utc": datetime.now(timezone.utc).isoformat(),
        "exit_code": result.returncode,
    })
    print(result.stdout[-4500:], flush=True)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["init", "test", "eval", "cli", "compare", "prepare", "probe", "diagnose"])
    parser.add_argument("--label", required=True)
    parser.add_argument("--backend", choices=["extractive", "gemma"], default="extractive")
    parser.add_argument("--retrieval", choices=["lexical", "embeddings"], default="lexical")
    parser.add_argument("--question")
    parser.add_argument("--before")
    parser.add_argument("--after")
    parser.add_argument("--tests", nargs="*")
    args = parser.parse_args()
    if args.action == "init":
        tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
        write_json(HERE / "baseline-manifest.json", {
            "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip(),
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "client_date": "2026-10-21", "timezone": "Europe/Belgrade",
            "tracked_sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
                               for p in tracked if p and (ROOT / p).is_file()},
        })
        return 0
    if args.action == "test":
        temporary = HERE / "_pytest" / args.label
        if temporary.exists():
            raise FileExistsError("Use a fresh test label.")
        temporary.parent.mkdir(exist_ok=True)
        command = [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "--basetemp", str(temporary),
                   *(args.tests or [])]
        return execute(args.label, command)
    if args.action == "prepare":
        return execute(args.label, [sys.executable, "-m", "src.prepare_embeddings"], offline_model=False)
    if args.action == "probe":
        return execute(args.label, [sys.executable, str(HERE / "model_probe.py")], retrieval="embeddings")
    if args.action == "diagnose":
        return execute(args.label, [sys.executable, "-c", PACED_MODULE, str(HERE / "citation_probe.py")],
                       backend="gemma", retrieval="embeddings", trace=True)
    if args.action in ("eval", "cli"):
        module = "src.eval_runner" if args.action == "eval" else "src.cli"
        command = ([sys.executable, "-c", PACED_MODULE, module] if args.backend == "gemma"
                   else [sys.executable, "-m", module])
        if args.action == "eval":
            output = HERE / (args.label + ".json")
            if output.exists():
                raise FileExistsError(output.name)
            command += ["--out", str(output)]
        else:
            if not args.question:
                parser.error("cli requires --question")
            command += ["--question", args.question, "--show-retrieved"]
        return execute(args.label, command, backend=args.backend, retrieval=args.retrieval, trace=True)
    if not args.before or not args.after:
        parser.error("compare requires --before and --after")
    return execute(args.label, [sys.executable, "-m", "src.eval_compare", args.before, args.after])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    raise SystemExit(main())
