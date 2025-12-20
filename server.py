
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app, supports_credentials=True)

# -----------------------------
# Ініціалізація бази даних
# -----------------------------
def init_db():
    conn = sqlite3.connect("acaunts, metadata.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_user(email, password_hash):
    conn = sqlite3.connect("acaunts, metadata.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, password_hash))
    conn.commit()
    conn.close()

def get_user(email):
    conn = sqlite3.connect("acaunts, metadata.db")
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE email = ?", (email,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

# -----------------------------
# Захист від brute-force
# -----------------------------
ATTEMPTS = {}
MAX_ATTEMPTS = 5
WINDOW_SECONDS = 900   # 15 хвилин
LOCK_SECONDS = 600     # 10 хвилин

def now():
    return datetime.utcnow()

def get_attempt(login):
    if login not in ATTEMPTS:
        ATTEMPTS[login] = {"attempts": 0, "first_attempt": None, "lock_until": None}
    return ATTEMPTS[login]

def is_locked(rec):
    return rec["lock_until"] and now() < rec["lock_until"]

def reset_attempts(rec):
    rec["attempts"] = 0
    rec["first_attempt"] = None
    rec["lock_until"] = None

def register_fail(rec):
    t = now()
    if rec["first_attempt"] is None or (t - rec["first_attempt"]).total_seconds() > WINDOW_SECONDS:
        rec["attempts"] = 1
        rec["first_attempt"] = t
    else:
        rec["attempts"] += 1
    if rec["attempts"] >= MAX_ATTEMPTS:
        rec["lock_until"] = t + timedelta(seconds=LOCK_SECONDS)

# -----------------------------
# Маршрути
# -----------------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("login", "").strip().lower()
    password = data.get("password", "")

    if not email or not password or "@" not in email:
        return jsonify({"error": "Вкажіть валідний email і пароль"}), 400

    if get_user(email):
        return jsonify({"error": "Користувач вже існує"}), 409

    add_user(email, generate_password_hash(password))
    return jsonify({"message": "Реєстрація успішна", "login": email}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("login", "").strip().lower()
    password = data.get("password", "")

    rec = get_attempt(email)
    if is_locked(rec):
        return jsonify({"error": "Акаунт тимчасово заблоковано"}), 429

    user_hash = get_user(email)
    if not user_hash or not check_password_hash(user_hash, password):
        register_fail(rec)
        return jsonify({"error": "Невірні облікові дані"}), 401

    reset_attempts(rec)
    return jsonify({"message": "success", "login": email}), 200

# -----------------------------
# Запуск сервера
# -----------------------------
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
