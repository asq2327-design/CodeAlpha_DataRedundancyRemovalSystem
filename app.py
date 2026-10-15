from flask import Flask, render_template, request, jsonify
import sqlite3
import hashlib
import difflib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data.db"

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                content_hash TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def normalize(text: str) -> str:
    return " ".join(text.strip().lower().split())


def content_hash(text: str) -> str:
    return hashlib.sha256(normalize(text).encode("utf-8")).hexdigest()


def find_match(text: str):
    normalized = normalize(text)
    new_hash = content_hash(text)
    with get_db() as conn:
        exact = conn.execute(
            "SELECT * FROM records WHERE content_hash = ?", (new_hash,)
        ).fetchone()
        if exact:
            return {
                "type": "redundant",
                "score": 1.0,
                "record": dict(exact)
            }

        rows = conn.execute("SELECT * FROM records ORDER BY id DESC").fetchall()

    best = None
    best_score = 0.0
    for row in rows:
        score = difflib.SequenceMatcher(
            None, normalized, normalize(row["content"])
        ).ratio()
        if score > best_score:
            best_score = score
            best = row

    if best and best_score >= 0.90:
        return {
            "type": "redundant",
            "score": round(best_score, 4),
            "record": dict(best)
        }

    if best and best_score >= 0.70:
        return {
            "type": "possible_duplicate",
            "score": round(best_score, 4),
            "record": dict(best)
        }

    return {
        "type": "unique",
        "score": round(best_score, 4),
        "record": dict(best) if best else None
    }


@app.route("/")
def index():
    with get_db() as conn:
        records = conn.execute(
            "SELECT * FROM records ORDER BY id DESC"
        ).fetchall()
    return render_template("index.html", records=records)


@app.post("/api/validate")
def validate():
    data = request.get_json(silent=True) or {}
    text = str(data.get("content", "")).strip()
    if not text:
        return jsonify({"error": "Content is required."}), 400

    result = find_match(text)
    return jsonify(result)


@app.post("/api/records")
def add_record():
    data = request.get_json(silent=True) or {}
    text = str(data.get("content", "")).strip()
    if not text:
        return jsonify({"error": "Content is required."}), 400

    result = find_match(text)
    if result["type"] != "unique":
        return jsonify({
            "status": "rejected",
            "reason": result["type"],
            "match": result
        }), 409

    record_hash = content_hash(text)
    try:
        with get_db() as conn:
            cursor = conn.execute(
                "INSERT INTO records (content, content_hash) VALUES (?, ?)",
                (text, record_hash)
            )
            record_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        return jsonify({
            "status": "rejected",
            "reason": "redundant"
        }), 409

    return jsonify({
        "status": "accepted",
        "id": record_id,
        "message": "Unique and verified data appended."
    }), 201


@app.get("/api/records")
def list_records():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM records ORDER BY id DESC"
        ).fetchall()
    return jsonify([dict(row) for row in rows])


@app.post("/api/records/clear")
def clear_records():
    with get_db() as conn:
        conn.execute("DELETE FROM records")
    return jsonify({"status": "cleared"})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
