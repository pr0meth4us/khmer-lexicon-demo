import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from checker import Checker
from samples import SAMPLES

BASE = Path(__file__).resolve().parent
DATA = Path(os.environ.get("LEXICON_PATH", BASE / "data" / "unified_lexicon.json"))
MAX_CHARS = 8000

app = Flask(__name__)

# Built once at boot: parsing 5.9k entries and building the automaton takes
# ~150 ms, and the CRF model load takes ~2 s. Neither belongs in a request.
CHECK = Checker(DATA)
# Warm the CRF model AND both scan paths. Without this the first request reports
# cold-cache timings (100+ ms) and the counter panel tells a lie on the one run
# a reviewer is most likely to look at.
CHECK.check(SAMPLES[0]["text"])


@app.get("/")
def index():
    return render_template("index.html", about=CHECK.about(), samples=SAMPLES)


@app.post("/api/check")
def api_check():
    payload = request.get_json(silent=True) or {}
    text = payload.get("text", "")
    if not text.strip():
        return jsonify({"error": "empty text"}), 400
    if len(text) > MAX_CHARS:
        return jsonify({"error": f"text too long ({MAX_CHARS} character limit)"}), 400
    return jsonify(CHECK.check(text, use_segmenter=payload.get("segmenter", True)))


@app.get("/api/about")
def api_about():
    return jsonify(CHECK.about())


@app.get("/healthz")
def healthz():
    return jsonify({"ok": True, "entries": len(CHECK.entries)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=False)
