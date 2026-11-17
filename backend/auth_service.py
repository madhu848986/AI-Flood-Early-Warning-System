
import sqlite3
import hashlib
import secrets
import hmac
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "floodguard_users.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                mobile TEXT UNIQUE NOT NULL,
                address TEXT NOT NULL,
                latitude REAL,
                longitude REAL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS flood_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                risk_category TEXT NOT NULL,
                flood_probability REAL,
                message TEXT NOT NULL,
                status TEXT DEFAULT 'PENDING',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        300000
    ).hex()

    return password_hash, salt


def register_user(username, password, mobile, address):
    password_hash, salt = hash_password(password)

    try:
        with get_connection() as connection:
            cursor = connection.execute("""
                INSERT INTO users
                (username, password_hash, salt, mobile, address)
                VALUES (?, ?, ?, ?, ?)
            """, (username, password_hash, salt, mobile, address))

            return cursor.lastrowid

    except sqlite3.IntegrityError:
        return None


def login_user(username, password):
    with get_connection() as connection:
        user = connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if user is None:
            return None

        password_hash, _ = hash_password(password, user["salt"])

        if not hmac.compare_digest(
            password_hash,
            user["password_hash"]
        ):
            return None

        token = secrets.token_urlsafe(32)

        connection.execute("""
            INSERT INTO sessions (token, user_id)
            VALUES (?, ?)
        """, (token, user["id"]))

        return token


def get_user_by_token(token):
    with get_connection() as connection:
        return connection.execute("""
            SELECT users.id, users.username, users.mobile,
                   users.address, users.latitude, users.longitude
            FROM users
            JOIN sessions ON users.id = sessions.user_id
            WHERE sessions.token = ?
        """, (token,)).fetchone()


def update_user_location(user_id, latitude, longitude):
    with get_connection() as connection:
        connection.execute("""
            UPDATE users
            SET latitude = ?, longitude = ?
            WHERE id = ?
        """, (latitude, longitude, user_id))


def get_users_with_locations():
    with get_connection() as connection:
        return connection.execute("""
            SELECT id, username, mobile, address, latitude, longitude
            FROM users
            WHERE latitude IS NOT NULL
              AND longitude IS NOT NULL
        """).fetchall()


def create_flood_alert(
    user_id,
    risk_category,
    flood_probability,
    message
):
    with get_connection() as connection:

        existing_alert = connection.execute("""
            SELECT id
            FROM flood_alerts
            WHERE user_id = ?
              AND risk_category = ?
              AND status = 'PENDING'
            LIMIT 1
        """, (user_id, risk_category)).fetchone()

        if existing_alert:
            print(
                f"Duplicate pending alert skipped for user ID {user_id}."
            )
            return existing_alert["id"]

        cursor = connection.execute("""
            INSERT INTO flood_alerts
            (user_id, risk_category, flood_probability, message)
            VALUES (?, ?, ?, ?)
        """, (
            user_id,
            risk_category,
            flood_probability,
            message
        ))

        return cursor.lastrowid


def create_flood_alert_with_status(
    user_id,
    risk_category,
    flood_probability,
    message
):
    with get_connection() as connection:

        existing_alert = connection.execute("""
            SELECT id
            FROM flood_alerts
            WHERE user_id = ?
              AND risk_category = ?
              AND status = 'PENDING'
            LIMIT 1
        """, (user_id, risk_category)).fetchone()

        if existing_alert:
            print(
                f"Duplicate pending alert skipped for user ID {user_id}."
            )
            return existing_alert["id"], False

        cursor = connection.execute("""
            INSERT INTO flood_alerts
            (user_id, risk_category, flood_probability, message)
            VALUES (?, ?, ?, ?)
        """, (
            user_id,
            risk_category,
            flood_probability,
            message
        ))

        return cursor.lastrowid, True


def get_user_alerts(user_id):
    with get_connection() as connection:
        return connection.execute("""
            SELECT *
            FROM flood_alerts
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,)).fetchall()


def update_alert_status(alert_id, status):
    with get_connection() as connection:
        connection.execute("""
            UPDATE flood_alerts
            SET status = ?
            WHERE id = ?
        """, (status, alert_id))


def logout_user(token):
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM sessions WHERE token = ?",
            (token,)
        )
