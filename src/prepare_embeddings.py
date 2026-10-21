"""Explicitly prepare pinned public model files; never upload corpus text."""

import sys

from .retrieval_errors import RetrievalError
from .semantic_retrieval import model_identity


def main() -> int:
    try:
        identity = model_identity()
        try:
            from huggingface_hub import snapshot_download
        except ImportError:
            raise RetrievalError(
                "Install optional dependencies: python -m pip install -r requirements-embeddings.txt"
            ) from None
        snapshot_download(repo_id=identity.name, revision=identity.revision,
            cache_dir=identity.cache, allow_patterns=[
                "model.safetensors", "config.json", "modules.json", "config_sentence_transformers.json",
                "sentence_bert_config.json", "1_Pooling/config.json", "tokenizer.json",
                "tokenizer_config.json", "special_tokens_map.json", "vocab.txt", "README.md", "LICENSE",
            ])
    except RetrievalError as error:
        print(str(error), file=sys.stderr)
        return 1
    except Exception:
        # Download exceptions can include authentication URLs/headers; keep them
        # out of console evidence while leaving model preparation an explicit error.
        print("Model preparation failed. Check network access and the configured pinned model revision.", file=sys.stderr)
        return 1
    print(f"Prepared {identity.name} at revision {identity.revision} in {identity.cache}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
