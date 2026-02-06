import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return {
        "service": "Why Did It Fail?",
        "status": "running"
    }

@app.route("/health")
def health():
    return {"status": "ok"}

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(force=True)
    raw_logs = data.get("logs", "")

    if not raw_logs.strip():
        return {
            "summary": "No logs provided.",
            "confidence": "none"
        }

    lines = [l.strip() for l in raw_logs.splitlines() if l.strip()]

    scored = []

    for i, line in enumerate(lines):
        score = 0
        upper = line.upper()

        if "ERROR" in upper or "EXCEPTION" in upper or "FAILED" in upper:
            score += 5
        if "WARN" in upper or "WARNING" in upper:
            score += 2

        # earlier lines matter more
        score += max(0, 3 - i // 10)

        scored.append((score, line))

    scored.sort(reverse=True, key=lambda x: x[0])

    if scored[0][0] == 0:
        return {
            "summary": "No clear failure signal detected.",
            "confidence": "low"
        }

    top = scored[0][1]

    return {
        "summary": "Most likely failure origin",
        "root_cause": top,
        "confidence": "medium" if scored[0][0] < 7 else "high",
        "note": "Result based on heuristic analysis of unstructured logs."
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
