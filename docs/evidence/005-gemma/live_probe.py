"""Two synthetic, non-eval live checks. Requires explicit Gemma opt-in and a key."""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src import config
from src.chunking import Chunk
from src.generation import validate_backend
from src.generation_errors import ConfigurationError, GenerationError
from src.rag import build_grounded_answer


def main() -> int:
    try:
        if config.ANSWER_BACKEND != "gemma":
            raise ConfigurationError("Select ANSWER_BACKEND=gemma before running the live probe.")
        validate_backend()
        chunks = [Chunk("probe-library-chunk-0", "probe-library", "Fictional library",
                        "2026", "current", "On Fridays, the library closes at 17:00.")]
        cases = [("When does the library close on Fridays?", False),
                 ("Does the library offer weekend childcare?", True)]
        passed = True
        for question, expected_refusal in cases:
            answer = build_grounded_answer(question, chunks)
            passed &= answer.refused is expected_refusal
            print(json.dumps({"question": question, "answer": answer.answer,
                              "citations": answer.citations, "refused": answer.refused,
                              "expected_refusal": expected_refusal}, ensure_ascii=False))
        print("Probe behavior checks passed; manually verify the 17:00 fact and citations."
              if passed else "Probe behavior checks failed; do not start the measured evaluation.")
        return 0 if passed else 1
    except GenerationError as error:
        print(f"Live probe failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
