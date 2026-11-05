
import json
import urllib.error
import urllib.request


class AdvisorError(Exception):
    pass


class MaintenanceAdvisor:
    def __init__(
        self,
        model="gemma3:4b",
        url="http://127.0.0.1:11434/api/chat",
        timeout=180,
    ):
        self.model = model
        self.url = url
        self.timeout = timeout

    def recommend(
        self,
        query: str,
        retrieved_documents: list[dict],
    ):
        if not retrieved_documents:
            raise AdvisorError(
                "No maintenance documents retrieved"
            )

        context = "\n\n".join(
            f"[{doc['id']}]\n{doc['text']}"
            for doc in retrieved_documents
        )

        prompt = f"""\
You are an industrial maintenance advisory assistant\
for a SIMULATED conveyor system.

Use only the retrieved maintenance documents below.

You must not authorize a machine restart.
You must not claim that a physical machine is safe.

User fault description:
{query}

Retrieved documents:
{context}

Return JSON with exactly these fields:
{{
  "suspected_issue": "short description",
  "recommended_checks": ["check 1", "check 2"],
  "procedure_ids": ["PROC-001"],
  "limitations": "what cannot be confirmed"
}}

Rules:
- Use only the supplied procedures.
- Do not invent steps or measurements.
- Cite only procedure IDs present in the context.
- Do not recommend bypassing safety devices.
- Physical intervention requires authorized
  personnel and approved isolation procedures.
- The deterministic controller and operator
  retain all restart authority.
- Return JSON only.
"""

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
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

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout,
            ) as response:
                result = json.load(response)

            report = json.loads(
                result["message"]["content"]
            )

        except (
            urllib.error.URLError,
            TimeoutError,
            OSError,
            KeyError,
            ValueError,
            TypeError,
        ) as exc:
            raise AdvisorError(
                f"Maintenance generation failed: {exc}"
            ) from exc

        if not isinstance(report, dict):
            raise AdvisorError(
                "Advisor response must be an object"
            )

        if not isinstance(
            report.get("suspected_issue"), str
        ):
            raise AdvisorError(
                "Invalid suspected issue"
            )

        if (
            not isinstance(
                report.get("recommended_checks"), list
            )
            or not all(
                isinstance(item, str)
                for item in report["recommended_checks"]
            )
        ):
            raise AdvisorError(
                "Invalid recommended checks"
            )

        if not isinstance(
            report.get("procedure_ids"), list
        ):
            raise AdvisorError(
                "Invalid procedure citations"
            )

        allowed_ids = {
            doc["id"] for doc in retrieved_documents
        }

        if not all(
            isinstance(item, str)
            and item in allowed_ids
            for item in report["procedure_ids"]
        ):
            raise AdvisorError(
                "Advisor cited an unknown procedure"
            )

        if not isinstance(
            report.get("limitations"), str
        ):
            raise AdvisorError(
                "Invalid limitations"
            )

        return report
