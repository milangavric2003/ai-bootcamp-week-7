"""Inject local primary timeouts, then make a real Google fallback request.

The injected failures never reach Google. They verify recovery without waiting
for a real outage or sending deliberately bad requests. No fixed-eval quality
claim is made by this operational probe.
"""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from src import config, gemma_client
from src.generation_errors import ConfigurationError, GenerationError
from src.rag import answer_question


def main() -> int:
    original_open = gemma_client._open
    primary_failures = 0
    try:
        if config.ANSWER_BACKEND != "gemma" or not config.GEMMA_FALLBACK_MODEL:
            raise ConfigurationError("Select Gemma with an enabled fallback before running this probe.")

        def injected_open(request, timeout):
            nonlocal primary_failures
            model = request.full_url.split("/models/")[1].split(":")[0]
            if model == config.GEMMA_MODEL:
                primary_failures += 1
                raise TimeoutError("Synthetic local timeout; no Google request was sent.")
            return original_open(request, timeout=timeout)

        gemma_client._open = injected_open
        answer = answer_question("What is the parental leave policy?")
        print(json.dumps({"probe": "locally injected primary timeouts, real fallback",
                          "injected_primary_failures": primary_failures,
                          "model": answer.model, "attempts": answer.attempts,
                          "answer": answer.answer, "citations": answer.citations,
                          "refused": answer.refused}, ensure_ascii=False))
        if primary_failures != 2 or answer.model != config.GEMMA_FALLBACK_MODEL or not answer.refused:
            print("Fallback probe did not meet the expected recovery/refusal contract.", file=sys.stderr)
            return 1
        return 0
    except GenerationError as error:
        print(f"Fallback probe failed: {error}", file=sys.stderr)
        return 1
    finally:
        gemma_client._open = original_open


if __name__ == "__main__":
    raise SystemExit(main())
