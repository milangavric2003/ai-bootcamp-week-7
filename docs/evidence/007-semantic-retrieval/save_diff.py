"""Save the reviewed source diff without staging or committing any files."""

import difflib
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
tracked = ["src/config.py", "src/retrieval.py", "src/cli.py", "tests/conftest.py", ".env.example", "README.md"]
created = ["src/semantic_retrieval.py", "src/retrieval_errors.py", "src/prepare_embeddings.py",
           "tests/test_semantic_retrieval.py", "requirements-embeddings.txt"]
patch = subprocess.check_output(["git", "--no-pager", "diff", "--no-ext-diff", "HEAD", "--", *tracked],
                                cwd=ROOT, timeout=15).decode("utf-8")
for name in created:
    patch += f"diff --git a/{name} b/{name}\nnew file mode 100644\n"
    patch += "".join(difflib.unified_diff([], (ROOT / name).read_text(encoding="utf-8").splitlines(keepends=True),
                                        fromfile="/dev/null", tofile="b/" + name))
with (HERE / "implementation.diff").open("x", encoding="utf-8") as stream:
    stream.write(patch)
print("Saved tracked and new source/config/test/setup changes.")
