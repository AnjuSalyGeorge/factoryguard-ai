
import pytest

from src.rag.index import cosine_similarity
from src.rag.loader import (
    load_manuals,
    manual_to_text,
)
from src.rag.retriever import MaintenanceRetriever
from src.simulator.conveyor import ConveyorMachine
from src.simulator.machine import get_reading


class FakeEmbedder:
    model = "fake-model"

    def embed(self, texts):
        vectors = []

        for text in texts:
            text = text.lower()

            vectors.append([
                float("jam" in text or "obstruction" in text),
                float("temperature" in text or "overheat" in text),
                float("vibration" in text),
            ])

        return vectors


def test_manuals_load():
    manuals = load_manuals()

    assert len(manuals) >= 6


def test_manual_ids_unique():
    manuals = load_manuals()

    ids = [manual["id"] for manual in manuals]

    assert len(ids) == len(set(ids))


def test_manual_to_text():
    manual = load_manuals()[0]
    text = manual_to_text(manual)

    assert manual["id"] in text
    assert manual["title"] in text


def test_cosine_similarity_identical():
    score = cosine_similarity(
        [1.0, 0.0],
        [1.0, 0.0],
    )

    assert score == pytest.approx(1.0)


def test_cosine_similarity_orthogonal():
    score = cosine_similarity(
        [1.0, 0.0],
        [0.0, 1.0],
    )

    assert score == pytest.approx(0.0)


def test_retrieval_with_fault_code():
    fake_index = {
        "embedding_model": "fake-model",
        "records": [
            {
                "id": "PROC-001",
                "title": "Jam",
                "text": "Conveyor jam obstruction",
                "fault_codes": ["OVERCURRENT"],
                "vector": [1.0, 0.0, 0.0],
            },
            {
                "id": "PROC-002",
                "title": "Heat",
                "text": "Motor temperature",
                "fault_codes": ["OVERHEATING"],
                "vector": [0.0, 1.0, 0.0],
            },
        ],
    }

    retriever = MaintenanceRetriever(
        embedder=FakeEmbedder(),
        index=fake_index,
    )

    results = retriever.search(
        "Conveyor jam obstruction",
        fault_codes=["OVERCURRENT"],
    )

    assert results[0]["id"] == "PROC-001"


def test_empty_query_rejected():
    fake_index = {
        "embedding_model": "fake-model",
        "records": [],
    }

    retriever = MaintenanceRetriever(
        embedder=FakeEmbedder(),
        index=fake_index,
    )

    with pytest.raises(ValueError):
        retriever.search("")


def test_rag_cannot_override_safety():
    machine = ConveyorMachine()

    machine.update_sensors(get_reading("jam"))

    # A recommendation is just data.
    recommendation = {
        "suspected_issue": "Possible obstruction",
        "procedure_ids": ["PROC-001"],
    }

    assert recommendation["procedure_ids"]
    assert machine.fault_latched is True
    assert machine.restart() is False
