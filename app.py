from flask import Flask, request, jsonify, g
from flask_cors import CORS
import jwt
from datetime import datetime, timedelta
from functools import wraps
import os
import sys

# ===== CONFIGURATION =====
app = Flask(__name__)

# Secret key (loaded from Railway Variables)
app.config['SECRET_KEY'] = os.getenv(
    'SECRET_KEY',
    'super-secret-key-change-in-production'  # intentionally weak (LAB)
)

JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))

# Enable CORS (INTENTIONALLY OPEN - LAB PURPOSE)
CORS(
    app,
    origins=["*"],
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"]
)

# ===== DUMMY USER DATABASE (INTENTIONALLY INSECURE) =====
USERS = {
    "admin": {
        "username": "admin",
        "password": "password123",
        "email": "admin@example.com"
    },
    "user": {
        "username": "user",
        "password": "password123",
        "email": "user@example.com"
    }
}

# ===== JWT UTILITIES =====

def generate_token(username):
    try:
        payload = {
            "username": username,
            "iat": int(datetime.utcnow().timestamp()),
            "exp": int((datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)).timestamp())
        }
        return jwt.encode(payload, app.config['SECRET_KEY'], algorithm="HS256")
    except Exception as e:
        print(f"[v0] Token generation error: {e}", file=sys.stderr)
        return None


def verify_token(token):
    try:
        return jwt.decode(
            token,
            app.config['SECRET_KEY'],
            algorithms=["HS256"]
        )
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_token_from_header():
    auth = request.headers.get("Authorization", "")
    parts = auth.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        if not token:
            return jsonify({"success": False, "message": "Missing token"}), 401

        payload = verify_token(token)
        if not payload:
            return jsonify({"success": False, "message": "Invalid or expired token"}), 401

        g.username = payload.get("username")
        return f(*args, **kwargs)

    return decorated


# ===== ROUTES =====

@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "success": True,
        "service": "Hybrid Authentication Security Lab",
        "status": "running"
    }), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "success": True,
        "message": "Backend healthy",
        "timestamp": datetime.utcnow().isoformat()
    }), 200


@app.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return "", 204

    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "JSON required"}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")

    user = USERS.get(username)
    if not user or user["password"] != password:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

    token = generate_token(username)
    if not token:
        return jsonify({"success": False, "message": "Token generation failed"}), 500

    return jsonify({
        "success": True,
        "username": username,
        "token": token,
        "expiresIn": JWT_EXPIRATION_HOURS * 3600
    }), 200


@app.route("/protected", methods=["GET", "OPTIONS"])
@token_required
def protected():
    if request.method == "OPTIONS":
        return "", 204

    return jsonify({
        "success": True,
        "message": "Protected access granted",
        "username": g.username
    }), 200


@app.route("/verify", methods=["POST", "OPTIONS"])
def verify():
    if request.method == "OPTIONS":
        return "", 204

    data = request.get_json()
    token = data.get("token") if data else None

    if not token:
        return jsonify({"success": False, "valid": False}), 400

    payload = verify_token(token)
    if not payload:
        return jsonify({"success": False, "valid": False}), 401

    return jsonify({
        "success": True,
        "valid": True,
        "username": payload.get("username"),
        "iat": payload.get("iat"),
        "exp": payload.get("exp")
    }), 200


# ===== MAIN (LOCAL ONLY) =====
if __name__ == "__main__":
    print("[v0] Starting local dev server")

    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=os.getenv("FLASK_ENV") == "development"
    )
