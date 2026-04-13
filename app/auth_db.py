import sqlite3
import hashlib
import os
from datetime import datetime
from typing import Optional, Dict, List


DATABASE_PATH = "data/users.db"
REGISTROS_FILE = "data/registros.txt"


def save_to_txt(user: Dict):
    os.makedirs(os.path.dirname(REGISTROS_FILE), exist_ok=True)
    with open(REGISTROS_FILE, "a", encoding="utf-8") as f:
        f.write(f"=== Nuevo Registro ===\n")
        f.write(f"Usuario: {user.get('username', '')}\n")
        f.write(f"Email: {user.get('email', '')}\n")
        f.write(f"Teléfono: {user.get('phone', '')}\n")
        f.write(f"Nombre: {user.get('full_name', '')}\n")
        f.write(f"Fecha: {user.get('created_at', '')}\n")
        f.write(f"=====================\n\n")


def init_db():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            created_at TEXT NOT NULL,
            last_login TEXT,
            is_active INTEGER DEFAULT 1
        )
    """)
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(
    username: str, email: str, password: str, full_name: str = "", phone: str = ""
) -> Dict:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    password_hash = hash_password(password)
    created_at = datetime.now().isoformat()

    try:
        cursor.execute(
            "INSERT INTO users (username, email, phone, password_hash, full_name, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (username, email, phone, password_hash, full_name, created_at),
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()

        user_data = {
            "id": user_id,
            "username": username,
            "email": email,
            "phone": phone,
            "full_name": full_name,
            "created_at": created_at,
            "is_active": 1,
        }
        save_to_txt(user_data)

        return user_data
    except sqlite3.IntegrityError as e:
        conn.close()
        raise Exception(f"Usuario o email ya existe: {e}")


def verify_user(username: str, password: str) -> Optional[Dict]:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    password_hash = hash_password(password)

    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password_hash = ? AND is_active = 1",
        (username, password_hash),
    )
    user = cursor.fetchone()

    if user:
        cursor.execute(
            "UPDATE users SET last_login = ? WHERE id = ?",
            (datetime.now().isoformat(), user["id"]),
        )
        conn.commit()

    conn.close()

    if user:
        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "phone": user["phone"],
            "full_name": user["full_name"],
            "created_at": user["created_at"],
            "last_login": user["last_login"],
            "is_active": user["is_active"],
        }
    return None


def get_user_by_username(username: str) -> Optional[Dict]:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND is_active = 1", (username,)
    )
    user = cursor.fetchone()
    conn.close()

    if user:
        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "phone": user["phone"],
            "full_name": user["full_name"],
            "created_at": user["created_at"],
            "last_login": user["last_login"],
            "is_active": user["is_active"],
        }
    return None


def get_user_by_email(email: str) -> Optional[Dict]:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ? AND is_active = 1", (email,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "phone": user["phone"],
            "full_name": user["full_name"],
            "created_at": user["created_at"],
            "last_login": user["last_login"],
            "is_active": user["is_active"],
        }
    return None


def get_all_users() -> List[Dict]:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE is_active = 1 ORDER BY created_at DESC")
    users = cursor.fetchall()
    conn.close()

    return [
        {
            "id": u["id"],
            "username": u["username"],
            "email": u["email"],
            "phone": u["phone"],
            "full_name": u["full_name"],
            "created_at": u["created_at"],
            "last_login": u["last_login"],
        }
        for u in users
    ]


if __name__ == "__main__":
    init_db()
    print("Base de datos de usuarios inicializada")
