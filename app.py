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
    logs = data.get("logs", "")

    lines = logs.split("\n")
    errors = [line for line in lines if "ERROR" in line]

    if not errors:
        return {
            "summary": "No critical failure detected.",
            "confidence": "low"
        }

    return {
        "summary": "The failure most likely started here:",
        "root_cause": errors[0],
        "confidence": "high"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
