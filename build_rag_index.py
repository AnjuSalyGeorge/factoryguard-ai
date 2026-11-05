
from src.rag.index import build_index


index = build_index()

print("Embedding model:", index["embedding_model"])
print("Indexed procedures:", len(index["records"]))

for record in index["records"]:
    print(record["id"], record["title"])
