from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, func
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

db_path = os.path.join('/data', 'todo.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    todos = db.relationship('Todo', backref='category', lazy=True)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'completed': self.completed,
            'category': self.category.name if self.category else None
        }

def migrate_database():
    with app.app_context():
        result = db.session.execute(text("PRAGMA table_info(todo);"))
        columns = [row[1] for row in result]
        if 'category_id' not in columns:
            db.session.execute(text("ALTER TABLE todo ADD COLUMN category_id INTEGER REFERENCES category(id);"))
            db.session.commit()
            print("Added category_id column.")
        else:
            print("category_id column already exists.")

        default_categories = ['Work', 'Personal', 'Shopping', 'Other']
        for cat_name in default_categories:
            if not Category.query.filter_by(name=cat_name).first():
                db.session.add(Category(name=cat_name))
        db.session.commit()

migrate_database()

@app.template_filter('category_color')
def category_color(category_name):
    colors = {
        'Work': '#007bff',
        'Personal': '#28a745',
        'Shopping': '#ffc107',
        'Other': '#6c757d'
    }
    return colors.get(category_name, '#6c757d')

# --- Category management routes ---
@app.route('/categories')
def list_categories():
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)

@app.route('/category/add', methods=['POST'])
def add_category():
    name = request.form.get('name', '').strip()
    if name:
        if Category.query.filter_by(name=name).first():
            flash('Category already exists!', 'danger')
        else:
            db.session.add(Category(name=name))
            db.session.commit()
            flash(f'Category "{name}" created.', 'success')
    else:
        flash('Category name cannot be empty.', 'danger')
    return redirect(url_for('index'))

@app.route('/category/edit/<int:cat_id>', methods=['POST'])
def edit_category(cat_id):
    category = Category.query.get_or_404(cat_id)
    new_name = request.form.get('name', '').strip()
    if new_name and new_name != category.name:
        if Category.query.filter_by(name=new_name).first():
            flash('Category name already exists!', 'danger')
        else:
            category.name = new_name
            db.session.commit()
            flash(f'Category renamed to "{new_name}".', 'success')
    elif not new_name:
        flash('Category name cannot be empty.', 'danger')
    return redirect(url_for('index'))

@app.route('/category/delete/<int:cat_id>', methods=['POST'])
def delete_category(cat_id):
    category = Category.query.get_or_404(cat_id)
    if Todo.query.filter_by(category_id=cat_id).first():
        flash(f'Cannot delete "{category.name}" because tasks are using it.', 'danger')
    else:
        db.session.delete(category)
        db.session.commit()
        flash(f'Category "{category.name}" deleted.', 'success')
    return redirect(url_for('index'))

# --- Frontend routes ---
@app.route('/')
def index():
    search_query = request.args.get('q', '').strip()
    category_id = request.args.get('cat', 'all')

    query = Todo.query
    if search_query:
        query = query.filter(Todo.title.ilike(f'%{search_query}%'))
    if category_id != 'all':
        query = query.filter_by(category_id=int(category_id))

    todos = query.order_by(Todo.id.desc()).all()
    categories = Category.query.order_by(Category.name).all()

    # Compute task counts per category
    # Using subquery or raw SQL to get count per category
    # We'll do it via SQLAlchemy: get all categories and count tasks
    category_counts = {}
    for cat in categories:
        # Count total tasks in this category (both completed and incomplete)
        count = Todo.query.filter_by(category_id=cat.id).count()
        category_counts[cat.id] = count

    return render_template('index.html', todos=todos, categories=categories,
                           search_query=search_query, selected_category=category_id,
                           category_counts=category_counts)

@app.route('/add', methods=['POST'])
def add_todo_form():
    title = request.form.get('title')
    category_id = request.form.get('category')
    if title:
        new_todo = Todo(title=title)
        if category_id and category_id != 'none':
            new_todo.category_id = int(category_id)
        db.session.add(new_todo)
        db.session.commit()
    return redirect(url_for('index', q=request.args.get('q', ''), cat=request.args.get('cat', 'all')))

@app.route('/complete/<int:todo_id>', methods=['POST'])
def complete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    todo.completed = not todo.completed
    db.session.commit()
    return redirect(url_for('index', q=request.args.get('q', ''), cat=request.args.get('cat', 'all')))

@app.route('/edit/<int:todo_id>', methods=['POST'])
def edit_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    new_title = request.form.get('title')
    new_category_id = request.form.get('category')
    if new_title:
        todo.title = new_title
    if new_category_id and new_category_id != 'none':
        todo.category_id = int(new_category_id)
    elif new_category_id == 'none':
        todo.category_id = None
    db.session.commit()
    return redirect(url_for('index', q=request.args.get('q', ''), cat=request.args.get('cat', 'all')))

@app.route('/delete/<int:todo_id>', methods=['POST'])
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('index', q=request.args.get('q', ''), cat=request.args.get('cat', 'all')))

# Batch endpoints (unchanged)
@app.route('/batch/complete', methods=['POST'])
def batch_complete():
    task_ids = request.form.getlist('task_ids')
    if task_ids:
        Todo.query.filter(Todo.id.in_(task_ids)).update({Todo.completed: True}, synchronize_session=False)
        db.session.commit()
    return redirect(url_for('index', q=request.args.get('q', ''), cat=request.args.get('cat', 'all')))

@app.route('/batch/incomplete', methods=['POST'])
def batch_incomplete():
    task_ids = request.form.getlist('task_ids')
    if task_ids:
        Todo.query.filter(Todo.id.in_(task_ids)).update({Todo.completed: False}, synchronize_session=False)
        db.session.commit()
    return redirect(url_for('index', q=request.args.get('q', ''), cat=request.args.get('cat', 'all')))

@app.route('/batch/delete', methods=['POST'])
def batch_delete():
    task_ids = request.form.getlist('task_ids')
    if task_ids:
        Todo.query.filter(Todo.id.in_(task_ids)).delete(synchronize_session=False)
        db.session.commit()
    return redirect(url_for('index', q=request.args.get('q', ''), cat=request.args.get('cat', 'all')))

# --- JSON API routes (optional) ---
@app.route('/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    return jsonify([t.to_dict() for t in todos])

@app.route('/todos', methods=['POST'])
def add_todo_json():
    data = request.get_json()
    new_todo = Todo(title=data['title'], completed=data.get('completed', False))
    if 'category' in data:
        cat = Category.query.filter_by(name=data['category']).first()
        if cat:
            new_todo.category_id = cat.id
    db.session.add(new_todo)
    db.session.commit()
    return jsonify(new_todo.to_dict()), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
