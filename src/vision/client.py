
import base64
import json
import time
import urllib.error
import urllib.request
from pathlib import Path


class VisionError(Exception):
    """Raised when local visual inspection fails."""


class OllamaVisionClient:
    def __init__(
        self,
        model="gemma3:4b",
        url="http://127.0.0.1:11434/api/chat",
        timeout=180,
    ):
        self.model = model
        self.url = url
        self.timeout = timeout

    def inspect(self, image_path: str) -> dict:
        path = Path(image_path)

        if not path.is_file():
            raise VisionError(
                f"Image does not exist: {path}"
            )

        image_base64 = base64.b64encode(
            path.read_bytes()
        ).decode("ascii")

        prompt = """
You are a visual inspection assistant for a
SIMULATED industrial conveyor workcell.

Examine the image only.

Identify visible objects and any obvious
misalignment or obstruction.

Return a JSON object with exactly these keys:

{
  "scene_status": "normal|misaligned|obstruction|uncertain",
  "observations": ["visible fact 1", "visible fact 2"],
  "suspected_issue": "short explanation",
  "uncertainty": "short explanation of limitations"
}

Rules:
- Do not infer motor temperature or current from pixels.
- Do not claim that the machine is safe to restart.
- Do not invent invisible sensors or mechanical faults.
- If uncertain, use "uncertain".
- Return JSON only.
"""

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_base64],
                }
            ],
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0
            },
        }

        request = urllib.request.Request(
            self.url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        started = time.perf_counter()

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
            raise VisionError(
                f"Local model request failed: {exc}"
            ) from exc

        latency = time.perf_counter() - started

        try:
            content = result["message"]["content"]
            report = json.loads(content)
        except (KeyError, TypeError, ValueError) as exc:
            raise VisionError(
                "Model returned invalid JSON"
            ) from exc

        allowed_statuses = {
            "normal",
            "misaligned",
            "obstruction",
            "uncertain",
        }

        if not isinstance(report, dict):
            raise VisionError(
                "Inspection report must be an object"
            )

        if report.get("scene_status") not in allowed_statuses:
            raise VisionError(
                "Invalid scene status"
            )

        if (
            not isinstance(report.get("observations"), list)
            or not all(
                isinstance(item, str)
                for item in report["observations"]
            )
            or not isinstance(
                report.get("suspected_issue"), str
            )
            or not isinstance(
                report.get("uncertainty"), str
            )
        ):
            raise VisionError(
                "Inspection report has invalid fields"
            )

        report["model"] = self.model
        report["latency_seconds"] = round(latency, 2)
        report["image_path"] = str(path)

        return report
