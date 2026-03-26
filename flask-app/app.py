from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Database configuration – the file is in the shared volume
db_path = os.path.join('/data', 'todo.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'completed': self.completed
        }

# Create tables (for demonstration, we'll do it on first request)
with app.app_context():
    db.create_all()

# --- Frontend routes ---
@app.route('/')
def index():
    # Order by id descending so newest tasks appear first
    todos = Todo.query.order_by(Todo.id.desc()).all()
    return render_template('index.html', todos=todos)

@app.route('/add', methods=['POST'])
def add_todo_form():
    title = request.form.get('title')
    if title:
        new_todo = Todo(title=title)
        db.session.add(new_todo)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/complete/<int:todo_id>', methods=['POST'])
def complete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    todo.completed = not todo.completed  # toggle
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:todo_id>', methods=['POST'])
def edit_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    new_title = request.form.get('title')
    if new_title:
        todo.title = new_title
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:todo_id>', methods=['POST'])
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('index'))

# --- JSON API routes (optional) ---
@app.route('/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    return jsonify([t.to_dict() for t in todos])

@app.route('/todos', methods=['POST'])
def add_todo_json():
    data = request.get_json()
    new_todo = Todo(title=data['title'], completed=data.get('completed', False))
    db.session.add(new_todo)
    db.session.commit()
    return jsonify(new_todo.to_dict()), 201

@app.route('/batch/complete', methods=['POST'])
def batch_complete():
    task_ids = request.form.getlist('task_ids')
    if task_ids:
        Todo.query.filter(Todo.id.in_(task_ids)).update({Todo.completed: True}, synchronize_session=False)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/batch/incomplete', methods=['POST'])
def batch_incomplete():
    task_ids = request.form.getlist('task_ids')
    if task_ids:
        Todo.query.filter(Todo.id.in_(task_ids)).update({Todo.completed: False}, synchronize_session=False)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/batch/delete', methods=['POST'])
def batch_delete():
    task_ids = request.form.getlist('task_ids')
    if task_ids:
        Todo.query.filter(Todo.id.in_(task_ids)).delete(synchronize_session=False)
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
