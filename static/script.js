// ====================== Task Manager Frontend JavaScript (Improved) ======================

const API_URL = '/api/tasks';

// Load tasks when page loads
document.addEventListener('DOMContentLoaded', () => {
    loadTasks();
    
    document.getElementById('searchInput').addEventListener('input', loadTasks);
    document.getElementById('priorityFilter').addEventListener('change', loadTasks);
    document.getElementById('statusFilter').addEventListener('change', loadTasks);
});

async function loadTasks() {
    const search = document.getElementById('searchInput').value.trim();
    const priority = document.getElementById('priorityFilter').value;
    const status = document.getElementById('statusFilter').value;

    let url = API_URL;
    const params = new URLSearchParams();

    if (search) params.append('search', search);
    if (priority && priority !== 'All') params.append('priority', priority);
    if (status && status !== 'All') params.append('status', status);

    if (params.toString()) url += '?' + params.toString();

    try {
        const response = await fetch(url);
        const tasks = await response.json();
        renderTasks(tasks);
        document.getElementById('taskCount').textContent = `${tasks.length} tasks`;
    } catch (error) {
        console.error('Error loading tasks:', error);
        alert('Failed to load tasks. Is the server running?');
    }
}

function renderTasks(tasks) {
    const container = document.getElementById('taskList');
    container.innerHTML = '';

    if (tasks.length === 0) {
        container.innerHTML = `<div class="list-group-item text-center text-muted py-4">No tasks found.</div>`;
        return;
    }

    tasks.forEach(task => {
        const dueDateHtml = task.due_date ? 
            `<small class="text-muted">Due: ${task.due_date}</small>` : '';

        const priorityClass = task.priority === 'High' ? 'bg-danger' : 
                              task.priority === 'Medium' ? 'bg-warning text-dark' : 'bg-info';

        const card = document.createElement('div');
        card.className = `list-group-item list-group-item-action ${task.completed ? 'bg-light' : ''}`;
        card.innerHTML = `
            <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                    <h6 class="${task.completed ? 'text-decoration-line-through text-muted' : ''}">
                        ${task.title}
                    </h6>
                    ${task.description ? `<p class="mb-1 text-muted small">${task.description}</p>` : ''}
                    <div class="d-flex gap-2 align-items-center">
                        ${dueDateHtml}
                        <span class="badge ${priorityClass}">${task.priority}</span>
                        ${task.completed ? 
                            `<span class="badge bg-success">Completed</span>` : 
                            `<span class="badge bg-secondary">Pending</span>`}
                    </div>
                </div>
                
                <div class="btn-group btn-group-sm" role="group">
                    <button onclick="toggleComplete(${task.id}, ${!task.completed})" 
                            class="btn ${task.completed ? 'btn-warning' : 'btn-success'}">
                        ${task.completed ? 'Undo' : 'Complete'}
                    </button>
                    <button onclick="showEditModal(${task.id}, '${task.title.replace(/'/g, "\\'")}', '${(task.description || '').replace(/'/g, "\\'")}', '${task.due_date || ''}', '${task.priority}')" 
                            class="btn btn-primary">Edit</button>
                    <button onclick="deleteTask(${task.id})" 
                            class="btn btn-danger">Delete</button>
                </div>
            </div>
        `;
        container.appendChild(card);
    });
}

// Add new task
async function addTask() {
    const title = document.getElementById('titleInput').value.trim();
    const description = document.getElementById('descriptionInput').value.trim();
    const due_date = document.getElementById('dueDateInput').value;
    const priority = document.getElementById('priorityInput').value;

    if (!title) {
        alert("Task title is required!");
        return;
    }

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ title, description, due_date, priority })
        });

        if (response.ok) {
            document.getElementById('titleInput').value = '';
            document.getElementById('descriptionInput').value = '';
            document.getElementById('dueDateInput').value = '';
            loadTasks();
        } else {
            alert("Failed to add task");
        }
    } catch (error) {
        alert("Error connecting to server");
    }
}

// Toggle Complete / Undo
async function toggleComplete(id, newCompleted) {
    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ 
                completed: newCompleted 
            })
        });

        if (response.ok) {
            loadTasks();
        } else {
            alert("Failed to update task");
        }
    } catch (error) {
        alert("Error updating task");
    }
}

// Delete task
async function deleteTask(id) {
    if (!confirm("Are you sure you want to delete this task?")) return;

    try {
        const response = await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
        if (response.ok) loadTasks();
    } catch (error) {
        alert("Failed to delete task");
    }
}

// Show Edit Modal (Simple prompt version for now)
function showEditModal(id, title, description, due_date, priority) {
    const newTitle = prompt("Edit Task Title:", title);
    if (newTitle === null) return; // User cancelled

    const newDescription = prompt("Edit Description:", description || "");
    const newDueDate = prompt("Edit Due Date (YYYY-MM-DD):", due_date || "");
    const newPriority = prompt("Edit Priority (High/Medium/Low):", priority);

    if (!newTitle) {
        alert("Title cannot be empty");
        return;
    }

    updateTask(id, newTitle, newDescription, newDueDate, newPriority);
}

// Update task (used by edit)
async function updateTask(id, title, description, due_date, priority) {
    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                title: title,
                description: description,
                due_date: due_date || null,
                priority: priority,
                completed: false   // Reset to false when editing (optional)
            })
        });

        if (response.ok) {
            loadTasks();
        } else {
            alert("Failed to update task");
        }
    } catch (error) {
        alert("Error updating task");
    }
}

// Clear filters
function clearFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('priorityFilter').value = 'All';
    document.getElementById('statusFilter').value = 'All';
    loadTasks();
}