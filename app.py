"""
Week 4
Complete TODO 1-5 in order.
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_smorest import abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

# TODO 1: Import SQLAlchemy

app = Flask(__name__)

# TODO 1: Add configuration and create db instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# ── TODO 2: Create TodoModel ──────────────────────────────────────────────────
# Replace the in-memory list below with a SQLAlchemy model.
# Hint: refer to your Book API code from class.


# TodoModel represents a single todo item in the database. 
# It has fields for id, title, description, status, priority, and category_id (foreign key to CategoryModel).
class TodoModel(db.Model):
    __tablename__ = "todos"

    # ID is the primary key, auto-incrementing integer. 
    # Title is a required string, while description is optional. 
    # Status and priority are required strings. 
    # Category_id is an optional foreign key linking to the categories table.
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), nullable=False)
    priority = db.Column(db.String(20), nullable=False)

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)

    # Convert model instance into a dictionary for easy JSON serialization.
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "category_id": self.category_id
        }


# ── TODO 5: CategoryModel (leave commented out until TODO 5) ─────────────────

# CategoryModel represents a category that todos can belong to. It has an id, name, and a relationship to the TodoModel
class CategoryModel(db.Model):
    __tablename__ = "categories"
    id    = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(100), nullable=False)
    todos = db.relationship('TodoModel', backref='category', lazy=True)
    
    # Convert model instance into a dictionary for easy JSON serialization. It includes the count of todos in this category
    def to_dict(self):
        return {
            "id":         self.id,
            "name":       self.name,
            # In the back-end, the todo_count allows us to easily access the number of todos associated with this category without needing to perform additional queries on the client side. 
            # This is especially useful for displaying category summaries or counts in the UI.
            "todo_count": len(self.todos)
        }
    
# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/api/todos', methods=['GET'])
def get_todos():
    # TODO 3: Replace with TodoModel.query
    q = TodoModel.query

    # Status and priority filters are optional query parameters. If provided, they filter the results accordingly
    status_str = request.args.get('status')
    if status_str:
        q = q.filter(TodoModel.status == status_str)

    # Similarly, the priority filter checks for a 'priority' query parameter and filters the todos based on their priority level
    priority_str = request.args.get('priority')
    if priority_str:
        q = q.filter(TodoModel.priority == priority_str)


    # TODO 5: Add category_id filter
    category_id = request.args.get('category_id')
    if category_id:
        q = q.filter(TodoModel.category_id == int(category_id))

    return jsonify([todo.to_dict() for todo in q.all()])


@app.route('/api/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    # TODO 3: Replace with db.get_or_404(TodoModel, todo_id)
    todo = db.get_or_404(TodoModel, todo_id)
    return jsonify(todo.to_dict())


@app.route('/api/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({"error": "Title is required"}), 400

    # TODO 3: Replace with TodoModel object + db.session.add/commit
    # TODO 5: Add category_id=data.get('category_id')
    todo = TodoModel(
        title=data['title'],
        description=data.get('description', ''),
        status=data.get('status', 'pending'),
        priority=data.get('priority', 'medium'),
        category_id=data.get('category_id')
    )

    try:
        db.session.add(todo)      # Stage the new record
        db.session.commit()       # Save to database
    except IntegrityError as e:
        db.session.rollback()  # Undo any partial changes
        abort(400, description=e.detail)
    except SQLAlchemyError:
        db.session.rollback()  # Undo any partial changes
        abort(500, description="An error occurred while creating the todo")

    return jsonify(todo.to_dict()), 201


@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    # TODO 3: Replace with SQLAlchemy pattern

    # Retrieve a record by its primary key; if the record exists, return corresponding TodoModel instance
    # Otherwise automatically abort the request with a 404 Not Found error. This eliminates the need for manual checks and error handling for missing records. 
    todo = db.get_or_404(TodoModel, todo_id)
    if not todo:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json()
    for field in ['title', 'description', 'status', 'priority']:
        if field in data:
            setattr(todo, field, data[field])

    try:
        db.session.commit()       # Save to database
    except SQLAlchemyError as e:
        db.session.rollback()  # Undo any partial changes
        abort(500, description="An error occurred while updating the todo")
    return jsonify(todo.to_dict())


@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    # TODO 3: Replace with SQLAlchemy pattern
    todo = db.get_or_404(TodoModel, todo_id)
    if not todo:
        return jsonify({"error": "Not found"}), 404

    try:
        db.session.delete(todo)
        db.session.commit()      # Save to database
    except SQLAlchemyError as e:
        db.session.rollback()  # Undo any partial changes
        abort(500, description = "An error occurred while deleting the todo")

    return jsonify({"message": "Todo deleted"})


# ── TODO 5: Category Routes ────────────────
@app.route('/api/categories', methods=['GET'])
# Retrieve all categories. Return a list of categories as JSON, where each category includes its ID, name, and the count of todos in that category.
def get_categories():
    return jsonify([c.to_dict() for c in CategoryModel.query.all()])

@app.route('/api/categories/<int:cat_id>', methods=['GET'])
# Retrieve a category by its ID. If the category exists, return its details as JSON.
def get_category(cat_id):
    cat = db.get_or_404(CategoryModel, cat_id)
    return jsonify(cat.to_dict())
#
@app.route('/api/categories', methods=['POST'])
# Create a new category. The request body should contain a JSON object with a 'name' field. 
# If the name is missing, return a 400 error. 
# Otherwise, create a new CategoryModel instance, add it to the database session, commit the transaction, and return the created category
def create_category():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Name is required"}), 400
    cat = CategoryModel(name=data['name'])
    db.session.add(cat)
    db.session.commit()
    return jsonify(cat.to_dict()), 201


# TODO 4: Add this block
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
