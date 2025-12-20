from flask import Flask, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ====== ТЕСТОВИЙ КОРИСТУВАЧ ======
USERS = {
    "test": {
        "password_hash": generate_password_hash("123456")
    }
}

# ====== RATE LIMIT / БЛОКУВАННЯ ======
ATTEMPTS = {}
MAX_ATTEMPTS = 5
WINDOW_SECONDS = 900   # 15 хв
LOCK_SECONDS = 600     # 10 хв

def now():
    return datetime.utcnow()

def get_attempt(login):
    if login not in ATTEMPTS:
        ATTEMPTS[login] = {
            "attempts": 0,
            "first_attempt": None,
            "lock_until": None
        }
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

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    login = data.get("login", "")
    password = data.get("password", "")

    rec = get_attempt(login)

    # Перевірка блокування
    if is_locked(rec):
        return jsonify({"error": "Акаунт тимчасово заблоковано"}), 429

    user = USERS.get(login)
    if not user:
        register_fail(rec)
        return jsonify({"error": "Невірні облікові дані"}), 401

    if not check_password_hash(user["password_hash"], password):
        register_fail(rec)
        return jsonify({"error": "Невірні облікові дані"}), 401

    # Успішний вхід
    reset_attempts(rec)
    return jsonify({"message": "success", "login": login}), 200

# ====== Реєстрація ======

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    login = data.get("login", "")
    password = data.get("password", "")

    if not login or not password:
        return jsonify({"error": "Логін і пароль обов’язкові"}), 400

    if login in USERS:
        return jsonify({"error": "Користувач вже існує"}), 409

    USERS[login] = {
        "password_hash": generate_password_hash(password)
    }
    return jsonify({"message": "Реєстрація успішна", "login": login}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)