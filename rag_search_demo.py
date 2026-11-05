
from src.rag.retriever import MaintenanceRetriever


retriever = MaintenanceRetriever()

results = retriever.search(
    query=(
        "Conveyor has an obstruction, "
        "motor current is high and speed is low"
    ),
    fault_codes=["OVERCURRENT", "LOW_RPM"],
    top_k=3,
)

for rank, result in enumerate(results, start=1):
    print(
        f"{rank}. {result['id']} "
        f"{result['title']}"
    )
    print("Score:", result["ranking_score"])
    print(
        "Matched codes:",
        result["matched_fault_codes"]
    )
    print()
