
import json
from pathlib import Path


DEFAULT_MANUAL_PATH = Path(
    "data/manuals/conveyor_maintenance.json"
)


def load_manuals(path=DEFAULT_MANUAL_PATH):
    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Maintenance manual not found: {path}"
        )

    with path.open("r", encoding="utf-8") as file:
        manuals = json.load(file)

    if not isinstance(manuals, list):
        raise ValueError(
            "Maintenance manual must contain a list"
        )

    required = {
        "id",
        "title",
        "fault_codes",
        "keywords",
        "symptoms",
        "procedure",
        "restart_policy",
    }

    seen_ids = set()

    for manual in manuals:
        if not isinstance(manual, dict):
            raise ValueError("Invalid manual entry")

        if not required.issubset(manual):
            raise ValueError(
                f"Missing required manual fields: {manual}"
            )

        if manual["id"] in seen_ids:
            raise ValueError(
                f"Duplicate procedure ID: {manual['id']}"
            )

        seen_ids.add(manual["id"])

        for field in ("fault_codes", "keywords", "procedure"):
            if not isinstance(manual[field], list):
                raise ValueError(
                    f"{field} must be a list"
                )

    return manuals


def manual_to_text(manual):
    return "\n".join([
        f"Procedure ID: {manual['id']}",
        f"Title: {manual['title']}",
        "Fault codes: " + ", ".join(manual["fault_codes"]),
        "Keywords: " + ", ".join(manual["keywords"]),
        "Symptoms: " + manual["symptoms"],
        "Procedure:",
        *[
            f"{i}. {step}"
            for i, step in enumerate(
                manual["procedure"], start=1
            )
        ],
        "Restart policy: " + manual["restart_policy"],
    ])
