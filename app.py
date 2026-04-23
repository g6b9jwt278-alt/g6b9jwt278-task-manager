from flask import Flask, jsonify, request, render_template
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Get DATABASE_URL from Render environment
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set!")

def get_db_connection():
    """Connect to PostgreSQL using the DATABASE_URL"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.cursor_factory = RealDictCursor
        return conn
    except Exception as e:
        print("Database connection error:", e)
        raise

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            priority TEXT CHECK(priority IN ('High', 'Medium', 'Low')) NOT NULL DEFAULT 'Medium',
            completed BOOLEAN DEFAULT FALSE
        )
    ''')
    conn.commit()
    conn.close()

# ====================== API ROUTES ======================

# (Keep your existing routes here - add_task, get_tasks, etc.)

if __name__ == '__main__':
    init_db()
    print("=== Task Manager with PostgreSQL Started ===")
    print("Connected to:", DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else "Database")
    app.run(debug=True)

# ====================== API ROUTES ======================

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    search = request.args.get('search', '').strip()
    priority = request.args.get('priority')
    status = request.args.get('status')

    conn = get_db_connection()
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if search:
        query += " AND (title ILIKE %s OR description ILIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])
    if priority and priority != 'All':
        query += " AND priority = %s"
        params.append(priority)
    if status and status != 'All':
        completed_value = True if status == 'Completed' else False
        query += " AND completed = %s"
        params.append(completed_value)

    query += " ORDER BY completed ASC, due_date ASC, id DESC"

    tasks = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([dict(task) for task in tasks])

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description', '')
    due_date = data.get('due_date')
    priority = data.get('priority', 'Medium')

    if not title:
        return jsonify({"error": "Title is required"}), 400

    conn = get_db_connection()
    conn.execute('''
        INSERT INTO tasks (title, description, due_date, priority)
        VALUES (%s, %s, %s, %s)
    ''', (title, description, due_date, priority))
    conn.commit()
    conn.close()

    return jsonify({"message": "Task created"}), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    due_date = data.get('due_date')
    priority = data.get('priority')
    completed = data.get('completed')

    conn = get_db_connection()
    existing = conn.execute('SELECT * FROM tasks WHERE id = %s', (task_id,)).fetchone()
    if not existing:
        conn.close()
        return jsonify({"error": "Task not found"}), 404

    if title is None:
        title = existing['title']
    if description is None:
        description = existing['description']
    if due_date is None:
        due_date = existing['due_date']
    if priority is None:
        priority = existing['priority']
    if completed is None:
        completed = existing['completed']

    conn.execute('''
        UPDATE tasks 
        SET title = %s, description = %s, due_date = %s, priority = %s, completed = %s
        WHERE id = %s
    ''', (title, description, due_date, priority, completed, task_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Task updated"})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = %s', (task_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Task deleted"})

# ====================== SERVE FRONTEND ======================
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    init_db()
    print("=== Task Manager with PostgreSQL Started ===")
    app.run(debug=True)