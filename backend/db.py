
import os
import streamlit as st
import mysql.connector
import bcrypt
from dotenv import load_dotenv

load_dotenv()


def get_config(key, default=None):
    try:
        value = st.secrets.get(key)
        if value is not None:
            return value
    except Exception:
        pass

    return os.getenv(key, default)


def get_connection():
    return mysql.connector.connect(
        host=get_config("DB_HOST"),
        port=int(get_config("DB_PORT", "3306")),
        user=get_config("DB_USER"),
        password=get_config("DB_PASSWORD"),
        database=get_config("DB_NAME"),
        connection_timeout=10
    )


def test_connection():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE(), VERSION()")
        result = cursor.fetchone()
        return result[0], result[1]
    finally:
        conn.close()


def authenticate_user(role, email, password):

    tables = {
        "Student": ("STUDENT", "StudentID", "StudentName"),
        "Tutor": ("TUTOR", "TutorID", "TutorName"),
        "Admin": ("ADMIN", "AdminID", "AdminName")
    }

    if role not in tables:
        return None

    table, id_column, name_column = tables[role]

    conn = get_connection()

    try:
        cursor = conn.cursor(dictionary=True)

        query = f"""
            SELECT {id_column}, {name_column}, Email,
                   PasswordHash, AccountStatus
            FROM {table}
            WHERE Email = %s
            LIMIT 1
        """

        cursor.execute(query, (email.strip(),))
        user = cursor.fetchone()

        if not user:
            return None

        if user["AccountStatus"].lower() != "active":
            return None

        if role == "Tutor" and not user.get("IsActive", 1):
            return None

        stored_hash = user["PasswordHash"]

        if not stored_hash:
            return None

        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode("utf-8")

        if not bcrypt.checkpw(
            password.encode("utf-8"),
            stored_hash
        ):
            return None

        return {
            "id": user[id_column],
            "name": user[name_column],
            "email": user["Email"],
            "role": role
        }

    finally:
        conn.close()
