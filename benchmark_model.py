
import json
import time
import urllib.request
import urllib.error


OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "gemma3:4b"


def main():
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": (
                    "In one sentence, explain what "
                    "a conveyor belt does."
                ),
            }
        ],
        "stream": False,
        "options": {
            "temperature": 0
        },
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    start = time.perf_counter()

    try:
        with urllib.request.urlopen(
            request, timeout=180
        ) as response:
            result = json.load(response)

    except (urllib.error.URLError, TimeoutError) as exc:
        print("Model request failed:", exc)
        return

    elapsed = time.perf_counter() - start

    print("MODEL:", MODEL)
    print("RESPONSE:", result["message"]["content"])
    print(f"Wall-clock latency: {elapsed:.2f} seconds")
    print(
        "Model-reported total duration:",
        round(result.get("total_duration", 0) / 1e9, 2),
        "seconds",
    )


if __name__ == "__main__":
    main()
