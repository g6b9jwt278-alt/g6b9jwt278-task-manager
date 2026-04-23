from flask import Flask, jsonify, request, render_template
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

DATABASE_URL = os.environ.get('DATABASE_URL')
print("DATABASE_URL loaded:", bool(DATABASE_URL))

def get_db_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set!")
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    conn = get_db_connection()
    tasks = conn.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(t) for t in tasks])

@app.route('/api/tasks', methods=['POST'])
def add_task():
    try:
        data = request.get_json()
        title = data.get('title')
        if not title:
            return jsonify({"error": "Title required"}), 400

        conn = get_db_connection()
        conn.execute("INSERT INTO tasks (title, priority) VALUES (%s, %s)", 
                    (title, data.get('priority', 'Medium')))
        conn.commit()
        conn.close()
        return jsonify({"message": "Task added"}), 201
    except Exception as e:
        print("Add Task Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)