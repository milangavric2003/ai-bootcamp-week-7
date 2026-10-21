"""Reuse the experiment runner with a fresh destination; preserve earlier evidence."""

import importlib.util
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
source = HERE.parent / "007-semantic-retrieval" / "run.py"
spec = importlib.util.spec_from_file_location("semantic_experiment_runner", source)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
runner.HERE = HERE

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    raise SystemExit(runner.main())
