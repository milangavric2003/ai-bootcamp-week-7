"""Capture one raw E09 model decision for diagnosis; no validator changes or score."""

import json
import os
from pathlib import Path

from src.gemma_client import GemmaClient
from src.generation_errors import GenerationError
from src.rag import answer_question

HERE = Path(__file__).resolve().parent
original = GemmaClient.generate
captured = {}


def capture(self, payload):
    result = original(self, payload)
    key = os.environ.get("GEMINI_API_KEY", "")
    captured.update(model=result.model,
                    raw_decision=result.text.replace(key, "[REDACTED]") if key else result.text)
    return result


GemmaClient.generate = capture
question = "Where do I request a replacement laptop and how long does it take?"
try:
    result = answer_question(question)
    captured.update(accepted=True, answer=result.answer, citations=result.citations)
except GenerationError as error:
    captured.update(accepted=False, error_type=type(error).__name__, error=str(error))
with (HERE / "e09-raw-decision.json").open("x", encoding="utf-8") as stream:
    json.dump(captured, stream, indent=2)
    stream.write("\n")
print(json.dumps(captured, indent=2))
