
import json
import urllib.error

import pytest

from src.vision.client import (
    OllamaVisionClient,
    VisionError,
)
from src.simulator.conveyor import (
    ConveyorMachine,
    ConveyorState,
)
from src.simulator.machine import get_reading


class FakeResponse:
    def __init__(self, content):
        self.payload = {
            "message": {
                "content": content
            }
        }

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(
            self.payload
        ).encode("utf-8")


# TEST 1: Missing image file
def test_missing_image():
    client = OllamaVisionClient()

    with pytest.raises(VisionError):
        client.inspect("missing_image.png")


# TEST 2: Invalid JSON returned by AI
def test_invalid_json(monkeypatch, tmp_path):
    image = tmp_path / "sample.png"
    image.write_bytes(b"test image")

    def fake_urlopen(*args, **kwargs):
        return FakeResponse("not valid json")

    monkeypatch.setattr(
        "urllib.request.urlopen",
        fake_urlopen,
    )

    client = OllamaVisionClient()

    with pytest.raises(VisionError):
        client.inspect(str(image))


# TEST 3: Valid structured AI response
def test_valid_structured_response(monkeypatch, tmp_path):
    image = tmp_path / "sample.png"
    image.write_bytes(b"test image")

    valid_report = {
        "scene_status": "obstruction",
        "observations": [
            "An unusual object is visible"
        ],
        "suspected_issue": "Possible obstruction",
        "uncertainty": "Still image only",
    }

    def fake_urlopen(*args, **kwargs):
        return FakeResponse(
            json.dumps(valid_report)
        )

    monkeypatch.setattr(
        "urllib.request.urlopen",
        fake_urlopen,
    )

    client = OllamaVisionClient()
    report = client.inspect(str(image))

    assert report["scene_status"] == "obstruction"


# TEST 4: Ollama service unavailable
def test_unavailable_model(monkeypatch, tmp_path):
    image = tmp_path / "sample.png"
    image.write_bytes(b"test image")

    def fake_urlopen(*args, **kwargs):
        raise urllib.error.URLError(
            "Connection refused"
        )

    monkeypatch.setattr(
        "urllib.request.urlopen",
        fake_urlopen,
    )

    client = OllamaVisionClient()

    with pytest.raises(VisionError):
        client.inspect(str(image))


# TEST 5: AI failure must not clear conveyor fault
def test_ai_failure_does_not_clear_fault():
    machine = ConveyorMachine()

    machine.update_sensors(get_reading("jam"))

    # Simulate an AI inspection failure.
    try:
        raise VisionError("Simulated AI failure")
    except VisionError:
        pass

    assert machine.state == ConveyorState.STOPPED_FAULT
    assert machine.fault_latched is True
    assert machine.restart() is False


# TEST 6: Model request timeout
def test_model_timeout(monkeypatch, tmp_path):
    image = tmp_path / "sample.png"
    image.write_bytes(b"test image")

    def fake_urlopen(*args, **kwargs):
        raise TimeoutError("Model request timed out")

    monkeypatch.setattr(
        "urllib.request.urlopen",
        fake_urlopen,
    )

    client = OllamaVisionClient()

    with pytest.raises(
        VisionError,
        match="Local model request failed"
    ):
        client.inspect(str(image))


# TEST 7: Unsupported scene status
def test_unsupported_scene_status(monkeypatch, tmp_path):
    image = tmp_path / "sample.png"
    image.write_bytes(b"test image")

    invalid_report = {
        "scene_status": "machine_safe",
        "observations": [
            "A conveyor belt is visible"
        ],
        "suspected_issue": "No visible issue",
        "uncertainty": "Still image only",
    }

    def fake_urlopen(*args, **kwargs):
        return FakeResponse(
            json.dumps(invalid_report)
        )

    monkeypatch.setattr(
        "urllib.request.urlopen",
        fake_urlopen,
    )

    client = OllamaVisionClient()

    with pytest.raises(
        VisionError,
        match="Invalid scene status"
    ):
        client.inspect(str(image))
