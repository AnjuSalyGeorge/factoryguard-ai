
import json
import urllib.error
import urllib.request


class EmbeddingError(Exception):
    pass


class OllamaEmbedder:
    def __init__(
        self,
        model="nomic-embed-text",
        url="http://127.0.0.1:11434/api/embed",
        timeout=120,
    ):
        self.model = model
        self.url = url
        self.timeout = timeout

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        payload = {
            "model": self.model,
            "input": texts,
        }

        request = urllib.request.Request(
            self.url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout,
            ) as response:
                result = json.load(response)

        except (
            urllib.error.URLError,
            TimeoutError,
            OSError,
        ) as exc:
            raise EmbeddingError(
                f"Embedding request failed: {exc}"
            ) from exc

        vectors = result.get("embeddings")

        if (
            not isinstance(vectors, list)
            or len(vectors) != len(texts)
        ):
            raise EmbeddingError(
                "Unexpected embedding response"
            )

        for vector in vectors:
            if (
                not isinstance(vector, list)
                or not vector
                or not all(
                    isinstance(value, (int, float))
                    for value in vector
                )
            ):
                raise EmbeddingError(
                    "Invalid embedding vector"
                )

        return vectors
