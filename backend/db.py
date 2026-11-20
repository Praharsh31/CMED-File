import os
import mysql.connector
import bcrypt
from dotenv import load_dotenv

load_dotenv()
def get_connection():
    import streamlit as st

    def get_config(key, default=None):
        try:
            value = st.secrets.get(key)
            if value is not None:
                return value
        except Exception:
            pass

        return os.getenv(key, default)

    return mysql.connector.connect(
        host=get_config("DB_HOST"),
        port=int(get_config("DB_PORT", "3306")),
        user=get_config("DB_USER"),
        password=get_config("DB_PASSWORD"),
        database=get_config("DB_NAME"),
        connection_timeout=10
    )
