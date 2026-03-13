[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/h4oaXqdS)
# Lab 4

## Overview

In the in-class exploration, you converted a Book API from in-memory storage to SQLAlchemy with step-by-step guidance. In this lab you will do the same conversion yourself with a **Todo API**, then go one step further: connect Todos to **Categories** using a foreign key relationship.

| Task | What You Do | What You Learn |
|---|---|---|
| **TODO 1** | Configure Flask-SQLAlchemy | Database setup |
| **TODO 2** | Create TodoModel | Defining models |
| **TODO 3** | Update routes to use SQLAlchemy | CRUD with ORM |
| **TODO 4** | Add `db.create_all()` | Database initialization |
| **TODO 5** | Add foreign key to CategoryModel | Relationships between tables |

---

## Setup

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Running Tests

You do **not** need the server running to run tests.

```bash
pytest tests/ -v
```

Before you implement anything, you should see:

- `TestInMemoryAPI` → all PASS (starter API works)
- `TestSQLAlchemySetup` → FAIL
- `TestPersistentCRUD` → mostly PASS (in-memory version handles these), except `test_database_starts_empty` → FAIL
- `TestCategoryRelationship` → FAIL

After you complete all TODOs, all **25 tests** should PASS.

---

## Pre-Populated Data (In-Memory)

The starter code has 3 hardcoded todos:

| ID | Title | Status | Priority |
|---|---|---|---|
| 1 | Buy groceries | pending | medium |
| 2 | Finish homework | in_progress | high |
| 3 | Call dentist | done | low |

After your conversion, the database starts empty — data comes from POST requests.

---

## Part 1: SQLAlchemy Conversion

This is the same process you did in class with the Book API.

### TODO 1 — Configure Flask-SQLAlchemy (app.py)

At the top of `app.py`:

1. Import SQLAlchemy: `from flask_sqlalchemy import SQLAlchemy`
2. Add configuration:

| Config Key | Value |
|---|---|
| `SQLALCHEMY_DATABASE_URI` | `'sqlite:///todos.db'` |
| `SQLALCHEMY_TRACK_MODIFICATIONS` | `False` |

3. Create the db instance: `db = SQLAlchemy(app)`

---

### TODO 2 — Create the TodoModel (app.py)

Replace the `todos = [...]` list and `next_id` with a SQLAlchemy model.

**TodoModel:**

| Column | Type | Constraints |
|---|---|---|
| id | Integer | primary_key |
| title | String(200) | nullable=False |
| description | String(500) | |
| status | String(20) | default="pending" |
| priority | String(20) | default="medium" |

Your model needs:
- `__tablename__ = "todos"`
- A `to_dict()` method returning a dictionary of all fields

After TODO 1-2, run:

```bash
pytest tests/test_todo.py::TestSQLAlchemySetup -v
```

All 6 setup tests should PASS.

---

### TODO 3 — Update Routes (app.py)

Update each route to use SQLAlchemy. Use your Book API code from class as reference.

| Operation | SQLAlchemy Code |
|-----------|----------------|
| Get all | `TodoModel.query.all()` |
| Get by ID (or 404) | `db.get_or_404(TodoModel, id)` |
| Create | `db.session.add(obj)` then `db.session.commit()` |
| Update | Modify attributes, then `db.session.commit()` |
| Delete | `db.session.delete(obj)` then `db.session.commit()` |
| Filter | `TodoModel.query.filter_by(field=value)` |

---

### TODO 4 — Initialize the Database (app.py)

At the bottom of the file:

```python
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
```

After TODO 1-4, run:

```bash
pytest tests/test_todo.py::TestPersistentCRUD -v
```

All 7 CRUD tests should PASS.

---

## Part 2: Category Relationship

Now connect Todos to Categories using a foreign key. A `CategoryModel` is already provided in `app.py` (commented out) — you just need to uncomment it and wire things up.

**How the two tables relate:**

```
categories          todos
──────────          ──────────────────────
id  ◄───────────── category_id (FK)
name                title
                    status
                    priority
```

A Todo can belong to one Category. A Category can have many Todos.

### TODO 5 — Add Foreign Key + Relationship (app.py)

**Step 1:** Uncomment the `CategoryModel` class and the 3 category routes (`/api/categories`).

**Step 2:** Add a foreign key column to `TodoModel`:

```python
category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
```

**Step 3:** Update `TodoModel.to_dict()` to include `category_id`:

```python
"category_id": self.category_id,
```

**Step 4:** Update `create_todo` to accept `category_id`:

```python
category_id=data.get('category_id'),
```

**Step 5:** Update `get_todos` to support filtering by category:

```python
category_id = request.args.get('category_id')
if category_id:
    query = query.filter_by(category_id=int(category_id))
```

**Step 6:** Delete `instance/todos.db` and restart (the schema changed):

```bash
rm instance/todos.db
python app.py
```

After TODO 5, run:

```bash
pytest tests/test_todo.py::TestCategoryRelationship -v
```

All 8 category tests should PASS.

---

## File Guide

| File | What to Do |
|---|---|
| `app.py` | Implement TODO 1–5 |

---

## Submission

1. Complete all TODOs
2. Run `pytest tests/ -v` and verify all 25 tests pass
3. Push to your GitHub Classroom repository
4. Submit the repo link on bCourses