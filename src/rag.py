from dataclasses import dataclass
from time import perf_counter

from . import config
from .chunking import Chunk, build_chunks
from .corpus import load_corpus
from .generation import generate_answer, record_trace, validate_backend
from .generation_errors import GenerationError
from .retrieval import RetrievalResult, retrieve_top_k


REFUSAL_MESSAGE = "I do not have enough grounded evidence in the provided corpus to answer that question."


@dataclass(frozen=True)
class RagAnswer:
    answer: str
    citations: list[str]
    refused: bool
    retrieved: list[RetrievalResult]


def select_citations(results: list[RetrievalResult]) -> list[RetrievalResult]:
    if config.CITATION_MIN_SCORE is not None:
        raise NotImplementedError("CITATION_MIN_SCORE is not implemented yet.")
    return results


def build_grounded_answer(question: str, chunks: list[Chunk]) -> RagAnswer:
    started = perf_counter()
    results = []
    try:
        # Validate opt-in settings before retrieval, even for an eventual local refusal.
        validate_backend()
        results = retrieve_top_k(question, chunks)
        result, status, usage = _answer_from_results(question, results)
    except GenerationError as error:
        record_trace(question, results, None, "error", (perf_counter() - started) * 1000, error=error)
        raise
    record_trace(question, results, result, status, (perf_counter() - started) * 1000, usage=usage)
    return result


def _answer_from_results(question: str, results: list[RetrievalResult]) -> tuple[RagAnswer, str, dict]:
    if not results or results[0].score < config.REFUSAL_THRESHOLD:
        return RagAnswer(answer=REFUSAL_MESSAGE, citations=[], refused=True, retrieved=results), "local_refusal", {}

    if config.ANSWER_BACKEND == "gemma":
        decision = generate_answer(question, results)
        return RagAnswer(
            answer=REFUSAL_MESSAGE if decision.refused else decision.answer,
            citations=decision.citations, refused=decision.refused, retrieved=results,
        ), "complete", decision.usage or {}

    cited = select_citations(results)
    supporting_points = [f"[{item.chunk.chunk_id}] {item.chunk.text}" for item in cited]
    answer = "Grounded response based on retrieved context:\n" + "\n".join(supporting_points)
    return RagAnswer(
        answer=answer,
        citations=[item.chunk.chunk_id for item in cited],
        refused=False,
        retrieved=results,
    ), "complete", {}


def answer_question(question: str) -> RagAnswer:
    return build_grounded_answer(question, build_chunks(load_corpus()))
