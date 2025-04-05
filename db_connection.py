import streamlit as st
import mysql.connector
from mysql.connector.cursor import MySQLCursorDict

def get_db_connection():
    """
    Establish a database connection using Streamlit secrets.
    Ensures that the required table columns exist.
    Returns the database connection object or None if the connection fails.
    """
    try:
        conn = mysql.connector.connect(
            host=st.secrets["DB_HOST"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            database=st.secrets["DB_NAME"],
            connection_timeout=20
        )
        ensure_table_columns_exist(conn)
        return conn
    except mysql.connector.Error as err:
        st.error("Database connection error:")
        st.code(str(err), language="text")
        return None

def ensure_table_columns_exist(conn):
    """
    Ensures that the required columns exist in the 'movies' table.
    Adds any missing columns to the table.
    """
    if conn is None:
        st.warning("No connection available to ensure table columns.")
        return

    cursor = conn.cursor()
    
    required_columns = {
        "id": "INT AUTO_INCREMENT PRIMARY KEY",
        "title": "VARCHAR(255) NOT NULL",
        "genre": "VARCHAR(100)",
        "year": "INT(11)",
        "thumbnail": "TEXT",
        "video_url": "VARCHAR(500) NOT NULL",
        "description": "TEXT",
        "uploaded_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        "upload_date": "DATETIME DEFAULT CURRENT_TIMESTAMP",
        "views": "INT DEFAULT 0",
        "watch_count": "INT DEFAULT 0",
        "hidden": "TINYINT(1) DEFAULT 0",
        "likes": "INT DEFAULT 0"
    }

    try:
        # Create table if it doesn't exist (with only the id column initially)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                id INT AUTO_INCREMENT PRIMARY KEY
            );
        """)

        # Check existing columns
        cursor.execute("SHOW COLUMNS FROM movies")
        existing_columns = {row[0] for row in cursor.fetchall()}

        # Add missing columns
        for column, data_type in required_columns.items():
            if column not in existing_columns:
                alter_query = f"ALTER TABLE movies ADD COLUMN {column} {data_type};"
                cursor.execute(alter_query)
                st.info(f"Added missing column: {column}")

        conn.commit()
        st.success("Database structure verified and updated successfully.")
    except mysql.connector.Error as err:
        st.error("Error while ensuring table columns:")
        st.code(str(err), language="text")
    finally:
        cursor.close()

# Optional for local testing or debugging
if __name__ == "__main__":
    conn = get_db_connection()
    if conn:
        conn.close()
