
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.rag.retriever import MaintenanceRetriever


def main():
    cases = json.loads(
        (
            ROOT / "evaluation" / "day11_rag_queries.json"
        ).read_text(encoding="utf-8")
    )

    retriever = MaintenanceRetriever()
    results = []

    for case in cases:
        expected = set(
            case["expected_procedure_ids"]
        )

        if not expected:
            print(
                f"SKIP {case['id']}: "
                "Expected procedure ID not configured"
            )
            continue

        try:
            documents = retriever.search(
                query=case["query"],
                fault_codes=case["fault_codes"],
                top_k=3,
            )

            actual = [
                str(doc.get("id", ""))
                for doc in documents
            ]

            hit = bool(expected.intersection(actual))
            error = ""

        except Exception as exc:
            actual = []
            hit = False
            error = f"{type(exc).__name__}: {exc}"

        results.append({
            "case_id": case["id"],
            "expected_ids": ",".join(sorted(expected)),
            "retrieved_ids": ",".join(actual),
            "hit_at_3": hit,
            "error": error,
        })

        print(
            case["id"],
            "HIT" if hit else "MISS",
            actual,
        )

    if not results:
        raise SystemExit(
            "No labeled RAG cases available"
        )

    output = (
        ROOT / "evaluation" / "day11_rag_results.csv"
    )

    with output.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=results[0].keys()
        )
        writer.writeheader()
        writer.writerows(results)

    hits = sum(row["hit_at_3"] for row in results)

    print(
        f"\nRAG Hit@3: {hits}/{len(results)} "
        f"({hits / len(results):.1%})"
    )

    print("Saved:", output)


if __name__ == "__main__":
    main()
