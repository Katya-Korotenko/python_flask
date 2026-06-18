import sqlite3
import json
from flask import Flask, jsonify, request
from pydantic import ValidationError
from .registration import User
from .sql_queries import CREATE_TABLE, ALL_USERS, CREATE_USER

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('test.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    print("Initializing database...")
    with get_db() as conn:
        conn.execute(CREATE_TABLE)

@app.route('/')
def home():
    return 'Use links "/users"!'

@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'GET':
        with get_db() as conn:
            data = conn.execute(ALL_USERS).fetchall()
            users = []
            for row in data:
                row = dict(row)
                row["address"] = json.loads(row["address"])
                users.append(User(**row).model_dump())
            return jsonify(users)
    if request.method == 'POST':
        try:
            user = User(**request.get_json())
        except ValidationError as e:
            return jsonify({
                "error": str(e)
            }), 400

        with get_db() as conn:
            conn.execute(CREATE_USER, (
                user.name,
                user.age,
                user.email,
                json.dumps(user.address.model_dump()),
                user.is_employed,
                user.signup_ts
            )
            )
            conn.commit()

        return jsonify({'message': 'User created'}), 201




if __name__ == '__main__':
    init_db()
    app.run(debug=True)
