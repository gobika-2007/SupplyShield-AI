import json
import hashlib
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_FILE = BASE_DIR / "data" / "users.json"


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def load_users():
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        DATA_FILE.write_text("[]")

    try:
        return json.loads(DATA_FILE.read_text())
    except Exception:
        return []


def save_users(users):
    DATA_FILE.write_text(
        json.dumps(users, indent=2)
    )


def register_user(name: str, email: str, password: str):
    users = load_users()

    email = email.strip().lower()

    for user in users:
        if user["email"] == email:
            return {
                "success": False,
                "message": "An account with this email already exists."
            }

    new_user = {
        "id": len(users) + 1,
        "name": name.strip(),
        "email": email,
        "password": hash_password(password),
        "role": "Supply Chain Analyst"
    }

    users.append(new_user)
    save_users(users)

    return {
        "success": True,
        "message": "Account created successfully.",
        "user": {
            "id": new_user["id"],
            "name": new_user["name"],
            "email": new_user["email"],
            "role": new_user["role"]
        }
    }


def login_user(email: str, password: str):
    users = load_users()

    email = email.strip().lower()
    password_hash = hash_password(password)

    for user in users:
        if (
            user["email"] == email
            and user["password"] == password_hash
        ):
            return {
                "success": True,
                "message": "Login successful.",
                "user": {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"],
                    "role": user["role"]
                }
            }

    return {
        "success": False,
        "message": "Invalid email or password."
    }