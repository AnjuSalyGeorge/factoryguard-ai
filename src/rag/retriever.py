
from src.rag.embeddings import OllamaEmbedder
from src.rag.index import (
    cosine_similarity,
    load_index,
)


class MaintenanceRetriever:
    def __init__(self, embedder=None, index=None):
        self.embedder = embedder or OllamaEmbedder()
        self.index = index if index is not None else load_index()

        if (
            self.index["embedding_model"]
            != self.embedder.model
        ):
            raise ValueError(
                "Embedding model does not match index"
            )

    def search(
        self,
        query: str,
        fault_codes=None,
        top_k=3,
    ):
        if not query.strip():
            raise ValueError("Search query cannot be empty")

        if top_k < 1:
            raise ValueError("top_k must be positive")

        query_vector = self.embedder.embed([query])[0]
        fault_codes = set(fault_codes or [])

        results = []

        for record in self.index["records"]:
            semantic_score = cosine_similarity(
                query_vector,
                record["vector"],
            )

            matched_codes = sorted(
                fault_codes.intersection(
                    record["fault_codes"]
                )
            )

            # Modest deterministic boost for exact
            # sensor fault-code matches.
            code_boost = 0.15 if matched_codes else 0.0

            ranking_score = semantic_score + code_boost

            results.append({
                "id": record["id"],
                "title": record["title"],
                "text": record["text"],
                "semantic_score": round(
                    semantic_score, 4
                ),
                "ranking_score": round(
                    ranking_score, 4
                ),
                "matched_fault_codes": matched_codes,
            })

        results.sort(
            key=lambda item: item["ranking_score"],
            reverse=True,
        )

        return results[:top_k]
