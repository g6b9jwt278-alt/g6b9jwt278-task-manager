from flask import Flask, jsonify, request, render_template
import os
import sqlite3
from datetime import date

app = Flask(__name__)

# Use PostgreSQL on Render, SQLite locally
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    if DATABASE_URL:  # On Render
        import psycopg2
        from psycopg2.extras import RealDictCursor
        conn = psycopg2.connect(DATABASE_URL)
        conn.cursor_factory = RealDictCursor
        return conn
    else:  # On your computer
        conn = sqlite3.connect('tasks.db')
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    conn = get_db_connection()
    if DATABASE_URL:  # PostgreSQL
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                due_date TEXT,
                priority TEXT DEFAULT 'Medium',
                completed BOOLEAN DEFAULT FALSE
            )
        ''')
    else:  # SQLite
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                due_date TEXT,
                priority TEXT DEFAULT 'Medium',
                completed INTEGER DEFAULT 0
            )
        ''')
    conn.commit()
    conn.close()

# ====================== API ROUTES ======================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    conn = get_db_connection()
    tasks = conn.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(task) for task in tasks])

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    title = data.get('title')
    if not title:
        return jsonify({"error": "Title required"}), 400

    conn = get_db_connection()
    conn.execute("INSERT INTO tasks (title, priority, due_date) VALUES (?, ?, ?)", 
                (title, data.get('priority', 'Medium'), data.get('due_date')))
    conn.commit()
    conn.close()
    return jsonify({"message": "Task added"}), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    conn = get_db_connection()
    conn.execute("UPDATE tasks SET title = ?, due_date = ?, priority = ?, completed = ? WHERE id = ?", 
                (data.get('title'), data.get('due_date'), data.get('priority'), data.get('completed', True), task_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Updated"})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Deleted"})

if __name__ == '__main__':
    init_db()
    print("=== Task Manager Started ===")
    print("Using PostgreSQL" if DATABASE_URL else "Using SQLite (local)")
    app.run(debug=True)