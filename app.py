from dataclasses import dataclass
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

# create the extension
db = SQLAlchemy()
# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# initialize the app with the extension
db.init_app(app)

"""create models"""


@dataclass
class Todo(db.Model):
    id: int
    title: str
    done: bool

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    done = db.Column(db.Boolean)


@app.route('/create-db')
def create_db():
    with app.app_context():
        db.create_all()
    return 'create db'


"""
Endpoints
CRUD : Create, Read, Update, Delete
"""


@app.route('/todos', methods=['GET'])
def get_all_todos():
    todoList = Todo.query.all()
    return todoList


@app.route('/todos/<todo_id>', methods=['GET'])
def get_todo_by_id(todo_id):
    return 'GET TODO item by id : ' + todo_id


@app.route('/todos', methods=['POST'])
def create_todo():
    return 'Create a TODO item!'


@app.route('/todos/<todo_id>', methods=['PUT'])
def update_todo(todo_id):
    return 'Update a TODO item : ' + todo_id


@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    return 'Delete a TODO item : ' + todo_id


if __name__ == '__main__':
    app.run(debug=True)
