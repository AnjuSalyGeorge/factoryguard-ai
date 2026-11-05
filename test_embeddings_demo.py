
from src.rag.embeddings import OllamaEmbedder


embedder = OllamaEmbedder()

vectors = embedder.embed([
    "The conveyor motor is overheating.",
    "A foreign object is blocking the conveyor.",
])

print("Number of vectors:", len(vectors))
print("Vector dimensions:", len(vectors[0]))
print("First five values:", vectors[0][:5])
