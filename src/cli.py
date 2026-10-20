import argparse

from . import config
from .chunking import build_chunks
from .corpus import load_corpus
from .rag import build_grounded_answer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Week 7 RAG checkpoint")
    parser.add_argument("--question", required=True, help="Question to ask over the handbook")
    parser.add_argument("--show-retrieved", action="store_true", help="Also print retrieved chunks and scores")
    parser.add_argument("--retrieval-backend", choices=["lexical", "embeddings", "hybrid"],
                        default=config.RETRIEVAL_BACKEND, help="Retrieval method (default: lexical or RAG_RETRIEVAL_BACKEND)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config.RETRIEVAL_BACKEND = args.retrieval_backend
    chunks = build_chunks(load_corpus())
    by_id = {chunk.chunk_id: chunk for chunk in chunks}
    result = build_grounded_answer(args.question, chunks)

    print("Question:")
    print(args.question)
    print("\nAnswer:")
    print(result.answer)
    print("\nRefused:", result.refused)
    print("Citations:")
    if not result.citations:
        print("  None")
    for chunk_id in result.citations:
        chunk = by_id[chunk_id]
        print(f"  {chunk_id}: {chunk.title} (version {chunk.version}, {chunk.status})")

    if args.show_retrieved:
        print("\nRetrieved:")
        for item in result.retrieved:
            if item.semantic_score is not None:
                print(f"  RRF={item.score:.4f} cosine={item.semantic_score:.4f}  "
                      f"{item.chunk.chunk_id}: {item.chunk.text}")
            else:
                print(f"  {item.score:.4f}  {item.chunk.chunk_id}: {item.chunk.text}")


if __name__ == "__main__":
    main()
