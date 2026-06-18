CREATE_TABLE="""
    CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT NOT NULL,
            address ARRAY NOT NULL,
            is_employed BOOLEAN NOT NULL,
            signup_ts TIMESTAMP NOT NULL
        )"""

ALL_USERS="""
SELECT * FROM users
"""

CREATE_USER="""
            INSERT INTO users(name, age, email, address, is_employed, signup_ts ) VALUES (?, ?, ?, ?, ?, ?)
            """