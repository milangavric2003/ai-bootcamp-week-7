"""Replay the actual E09 decision before/after without making an API request."""

import importlib.util
from importlib.machinery import SourceFileLoader
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))

from src import generation
from src.chunking import build_chunks
from src.corpus import load_corpus
from src.generation_errors import InvalidResponseError
from src.retrieval import RetrievalResult

# .txt is deliberate evidence, not an importable application module.
baseline_spec = importlib.util.spec_from_loader("src._generation_before_group_fix",
    SourceFileLoader("src._generation_before_group_fix", str(HERE / "generation-before.py.txt")))
before = importlib.util.module_from_spec(baseline_spec)
sys.modules[baseline_spec.name] = before
baseline_spec.loader.exec_module(before)
raw = json.loads((HERE.parent / "007-semantic-retrieval/e09-raw-decision.json").read_text(encoding="utf-8"))["raw_decision"]
evidence = [RetrievalResult(chunk, 1.0) for chunk in build_chunks(load_corpus()) if chunk.doc_id == "hb-01"]
try:
    before.parse_decision(raw, evidence)
    raise AssertionError("Original parser unexpectedly accepted the captured failing decision")
except InvalidResponseError as error:
    old_error = str(error)
after = generation.parse_decision(raw, evidence)
value = {"before_error": old_error, "after_answer": after.answer,
         "after_citations": after.citations, "after_refused": after.refused}
with (HERE / "captured-decision-replay.json").open("x", encoding="utf-8") as stream:
    json.dump(value, stream, indent=2)
    stream.write("\n")
print(json.dumps(value, indent=2))
