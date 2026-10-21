"""Protect the existing uncommitted embeddings work and historical evidence."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def hashes():
    names = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    paths = {ROOT / name for name in names if name}
    for directory in [ROOT / "src", ROOT / "tests", ROOT / "specs/007-semantic-retrieval",
                      ROOT / "docs/evidence/007-semantic-retrieval"]:
        paths.update(p for p in directory.rglob("*") if p.is_file()
                     and "_pytest" not in p.parts and "__pycache__" not in p.parts
                     and p.name != "_last-request.txt")
    paths.update([ROOT / "requirements-embeddings.txt", ROOT / "docs/semantic-retrieval-report.md"])
    return {str(path.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(paths) if path.is_file()}


if __name__ == "__main__":
    manifest = HERE / "before-manifest.json"
    if "--capture" in sys.argv:
        value = {"commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip(),
                 "sha256": hashes()}
        with manifest.open("x", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2)
        with (HERE / "generation-before.py.txt").open("xb") as stream:
            stream.write((ROOT / "src/generation.py").read_bytes())
        print("Saved the current source and existing evidence hashes.")
    else:
        previous = json.loads(manifest.read_text(encoding="utf-8"))
        current = hashes()
        changed = [name for name, sha in previous["sha256"].items() if current.get(name) != sha]
        allowed = {"src/generation.py", "tests/test_generation.py", "README.md", "docs/semantic-retrieval-report.md"}
        assert set(changed) <= allowed, changed
        assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip() == previous["commit"]
        assert not subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT).strip()
        print(json.dumps({"protected_files": len(previous["sha256"]), "changed_files": changed,
                          "unchanged_earlier_evidence": True, "uncommitted_and_unstaged": True}, indent=2))
