
import json
import math
from pathlib import Path

from src.rag.loader import (
    load_manuals,
    manual_to_text,
)
from src.rag.embeddings import OllamaEmbedder


INDEX_PATH = Path("data/manuals/vector_index.json")


def cosine_similarity(a, b):
    if len(a) != len(b):
        raise ValueError("Vector dimensions differ")

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def build_index(
    output_path=INDEX_PATH,
    embedder=None,
):
    embedder = embedder or OllamaEmbedder()
    manuals = load_manuals()

    texts = [
        manual_to_text(manual)
        for manual in manuals
    ]

    vectors = embedder.embed(texts)

    records = []

    for manual, text, vector in zip(
        manuals, texts, vectors
    ):
        records.append({
            "id": manual["id"],
            "title": manual["title"],
            "text": text,
            "fault_codes": manual["fault_codes"],
            "vector": vector,
        })

    index = {
        "embedding_model": embedder.model,
        "records": records,
    }

    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True, exist_ok=True
    )

    with output_path.open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(index, file, indent=2)

    return index


def load_index(path=INDEX_PATH):
    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Vector index not found: {path}"
        )

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)
