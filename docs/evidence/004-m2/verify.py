"""Capture M2 provenance or verify integrity and the disabled baseline.

Run from the repository root with the project virtual environment.
This helper does not calculate or change evaluation metrics.
"""
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src import config
from src.eval_runner import format_table, run_eval
from src.retrieval import STOPWORDS


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_new(name: str, value: dict) -> None:
    with (EVIDENCE / name).open("x", encoding="utf-8") as output:
        output.write(json.dumps(value, indent=2) + "\n")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT).decode().strip()


def without_timestamp(run: dict) -> dict:
    return {key: value for key, value in run.items() if key != "created_at"}


if sys.argv[1:] == ["--capture"]:
    paths = git("ls-files", "--", "src", "tests", "eval", "results",
                "rag-week-7-weak-checkpoint", "week06", "specs", "docs/evidence").splitlines()
    before = json.loads((EVIDENCE / "before.json").read_text(encoding="utf-8"))
    previous = json.loads((ROOT / "results/after-m5.json").read_text(encoding="utf-8"))
    assert without_timestamp(before) == without_timestamp(previous)
    write_new("before-manifest.json", {
        "head": git("rev-parse", "HEAD"),
        "branch": git("branch", "--show-current"),
        "python": platform.python_version(),
        "config": config.snapshot(),
        "files": {path: sha(ROOT / path) for path in paths},
        "before_sha256": sha(EVIDENCE / "before.json"),
    })
    (EVIDENCE / "eval-before.txt").write_text(format_table(before) + "\n", encoding="utf-8")
    print("Baseline matches retained M1+M3+M5 except timestamp; manifest saved.")
elif sys.argv[1:] == ["--audit"]:
    docs = [ROOT / "README.md", ROOT / "docs/advanced-plan.md", ROOT / "docs/m2-report.md",
            *(ROOT / "specs/004-stopword-filter").rglob("*.md")]
    missing = [str(path.relative_to(ROOT)) + ": " + link
               for path in docs
               for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", path.read_text(encoding="utf-8"))
               if not link.startswith(("https:", "http:", "#"))
               and not (path.parent / link.split("#")[0]).exists()]
    assert not missing, missing
    tasks = (ROOT / "specs/004-stopword-filter/tasks.md").read_text(encoding="utf-8")
    assert len(re.findall(r"^- \[X\] T\d{3} ", tasks, re.M)) == 10
    assert not re.search(r"^- \[ \] T\d{3} ", tasks, re.M)
    plan = (ROOT / "specs/004-stopword-filter/plan.md").read_text(encoding="utf-8")
    frozen = re.search(r"```text\n(a an .*?)```", plan, re.S).group(1).split()
    assert len(frozen) == len(set(frozen)) == len(STOPWORDS) == 40
    assert set(frozen) == STOPWORDS
    assert config.STOPWORDS_ENABLED is False
    assert git("branch", "--show-current") == "main"
    print("Audit passed: local links resolve, all 10 tasks complete, frozen 40 words match, main retains M2=False.")
elif sys.argv[1:] in ([], ["--retained"]):
    retained = sys.argv[1:] == ["--retained"]
    manifest = json.loads((EVIDENCE / "before-manifest.json").read_text(encoding="utf-8"))
    changed = [path for path, old in manifest["files"].items() if sha(ROOT / path) != old]
    allowed = {"src/config.py", "src/retrieval.py", "tests/test_retrieval.py", "tests/test_rag.py"}
    assert set(changed) <= allowed, changed
    assert sha(EVIDENCE / "before.json") == manifest["before_sha256"]
    assert git("branch", "--show-current") == "main"
    target = "retained.json" if retained else "after.json"
    after = json.loads((EVIDENCE / target).read_text(encoding="utf-8"))
    before = json.loads((EVIDENCE / "before.json").read_text(encoding="utf-8"))
    assert config.snapshot() == after["config"]
    differences = {key for key in before["config"] if before["config"][key] != after["config"][key]}
    assert differences == (set() if retained else {"STOPWORDS_ENABLED"}), differences
    assert config.STOPWORDS_ENABLED is (not retained)
    original_enabled = config.STOPWORDS_ENABLED
    try:
        config.STOPWORDS_ENABLED = False
        reproduced = without_timestamp(run_eval()) == without_timestamp(before)
        assert reproduced, "Disabled M2 does not reproduce the saved baseline"
    finally:
        config.STOPWORDS_ENABLED = original_enabled
    write_new("retained-integrity.json" if retained else "after-integrity.json", {
        "branch": "main", "changed_tracked_experiment_files": changed,
        "other_manifest_files_unchanged": True,
        "baseline_json_unchanged": True,
        "disabled_filter_reproduces_baseline_except_timestamp": reproduced,
        "changed_settings": sorted(differences),
        "eval_set_sha256": sha(ROOT / "eval/eval_set.json"),
    })
    print("Integrity verified; disabled M2 reproduces the full baseline except timestamp.")
else:
    raise SystemExit("Usage: python docs/evidence/004-m2/verify.py [--capture|--retained|--audit]")
