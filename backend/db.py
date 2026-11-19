
import os
import mysql.connector
import bcrypt
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


def test_connection():
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE(), VERSION()")
        return cursor.fetchone()
    finally:
        connection.close()


def authenticate_user(role, email, password):
    tables = {
        "Student": ("STUDENT", "StudentID", "StudentName"),
        "Tutor": ("TUTOR", "TutorID", "TutorName"),
        "Admin": ("ADMIN", "AdminID", "AdminName")
    }

    if role not in tables:
        return None

    table, id_column, name_column = tables[role]

    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = f"""
            SELECT {id_column}, {name_column}, Email,
                   PasswordHash, AccountStatus
            FROM {table}
            WHERE Email = %s
            LIMIT 1
        """
        cursor.execute(query, (email.strip(),))
        user = cursor.fetchone()

        if not user or not user["PasswordHash"]:
            return None

        stored_hash = user["PasswordHash"]
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode("utf-8")

        if not bcrypt.checkpw(password.encode("utf-8"), stored_hash):
            return None

        if user["AccountStatus"] and user["AccountStatus"].lower() != "active":
            return None

        return {
            "id": user[id_column],
            "name": user[name_column],
            "email": user["Email"],
            "role": role
        }
    finally:
        connection.close()


def set_account_password(role, email, password):
    """Set a password for one existing account identified by role and email."""
    tables = {
        "Student": ("STUDENT", "StudentID"),
        "Tutor": ("TUTOR", "TutorID")
    }

    if role not in tables:
        raise ValueError("Password setup is only available for students and tutors.")

    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")

    table, id_column = tables[role]
    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            f"SELECT {id_column}, PasswordHash FROM {table} WHERE Email = %s LIMIT 1",
            (email.strip(),)
        )
        account = cursor.fetchone()

        if not account:
            raise ValueError("No account found with that email.")

        if account[1]:
            raise ValueError(
                "This account already has a password. "
                "Confirm before changing an existing password."
            )

        cursor.execute(
            f"UPDATE {table} SET PasswordHash = %s WHERE {id_column} = %s",
            (password_hash, account[0])
        )
        connection.commit()
        return True
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
