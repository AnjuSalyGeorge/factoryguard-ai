
import json

from src.vision.client import (
    OllamaVisionClient,
    VisionError,
)


def main():
    client = OllamaVisionClient()

    image_path = "data/scenarios/obstruction.png"

    print("FactoryGuard AI — Visual Inspection")
    print("Image:", image_path)
    print("Model:", client.model)

    try:
        report = client.inspect(image_path)
    except VisionError as exc:
        print("Inspection failed:", exc)
        return

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
