import mysql.connector
import os

def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Replace with your actual password
        database="movieverse_db",
        connection_timeout=10  # Set a timeout for the connection
    )
    ensure_table_columns_exist(conn)  # Ensure all columns exist before returning connection
    return conn

def ensure_table_columns_exist(conn):
    cursor = conn.cursor()

    # Define the required columns and their data types
    required_columns = {
        "id": "INT AUTO_INCREMENT PRIMARY KEY",
        "title": "VARCHAR(255) NOT NULL",
        "genre": "VARCHAR(100)",  # Added genre column
        "year": "INT(11)",
        "thumbnail": "TEXT",  # Added thumbnail column
        "video_url": "VARCHAR(500) NOT NULL",
        "description": "TEXT",
        "uploaded_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",  # Ensure timestamp column
        "upload_date": "DATETIME DEFAULT CURRENT_TIMESTAMP",
        "views": "INT DEFAULT 0",
        "watch_count": "INT DEFAULT 0",
        "hidden": "TINYINT(1) DEFAULT 0",  # Added hidden column
        "likes": "INT DEFAULT 0"
    }

    # Ensure the table exists
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
            print(f"Added missing column: {column}")

    conn.commit()
    cursor.close()
    print("Database structure verified and updated.")

# Run the function to ensure the database is properly structured
conn = get_db_connection()
conn.close()
