from flask import Flask, jsonify, request, render_template
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('tasks.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            priority TEXT CHECK(priority IN ('High', 'Medium', 'Low')) NOT NULL DEFAULT 'Medium',
            completed INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

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
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    if priority and priority != 'All':
        query += " AND priority = ?"
        params.append(priority)
    if status and status != 'All':
        completed_value = 1 if status == 'Completed' else 0
        query += " AND completed = ?"
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
        VALUES (?, ?, ?, ?)
    ''', (title, description, due_date, priority))
    conn.commit()
    new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()

    return jsonify({"message": "Task created", "id": new_id}), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    
    title = data.get('title')
    description = data.get('description')
    due_date = data.get('due_date')
    priority = data.get('priority')
    completed = data.get('completed')

    conn = get_db_connection()
    
    existing = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
    if not existing:
        conn.close()
        return jsonify({"error": "Task not found"}), 404

    if title is None:
        title = existing['title']
        description = existing['description']
        due_date = existing['due_date']
        priority = existing['priority']

    if priority is None:
        priority = existing['priority']

    conn.execute('''
        UPDATE tasks 
        SET title = ?, description = ?, due_date = ?, priority = ?, completed = ?
        WHERE id = ?
    ''', (title, description, due_date, priority, completed, task_id))
    
    conn.commit()
    conn.close()

    return jsonify({"message": "Task updated successfully"})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Task deleted"})

# ====================== SERVE FRONTEND ======================
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    init_db()
    print("=== Task Manager REST API Starting ===")
    print("Frontend → http://127.0.0.1:5000")
    print("API      → http://127.0.0.1:5000/api/tasks")
    app.run(debug=True)