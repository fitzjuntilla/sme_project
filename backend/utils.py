"""
Database utilities and helpers
"""
import os
import mysql.connector
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


def get_db_connection():
    """Get a database connection"""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


def log_activity(user_id, action, description=None):
    """Log user activity"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO activity_logs
            (user_id, action, description)
            VALUES (%s, %s, %s)
        """, (user_id, action, description))

        connection.commit()
        cursor.close()
        connection.close()

    except mysql.connector.Error:
        pass