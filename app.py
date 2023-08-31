from dataclasses import dataclass
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
app = Flask(__name__)

# create the extension
db = SQLAlchemy()
# create the app
app = Flask(__name__)
bcrypt = Bcrypt(app)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# initialize the app with the extension
db.init_app(app)

"""create models"""


@dataclass  # model is serializable
class Todo(db.Model):
    id: int
    title: str
    done: bool

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    done = db.Column(db.Boolean)


@dataclass
class User(db.Model):
    id: int
    email: str

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    #  todos = db.relationship('Todo', backref='user', lazy=True)


@app.route('/create-db')
def create_db():
    with app.app_context():
        #  db.drop_all()
        db.create_all()
    return 'create db'


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    #  hash password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    # todo try execpt for duplicate email

    return jsonify(new_user), 201


"""
Endpoints
CRUD : Create, Read, Update, Delete
"""


@app.route('/todos', methods=['GET'])
def get_all_todos():
    todo_list = Todo.query.all()
    return todo_list


@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo_by_id(todo_id):
    todo_item = Todo.query.filter_by(id=todo_id).first()
    if not todo_item:
        return jsonify({'message': 'No todo item found with id '
                        + str(todo_id)}), 404
    return jsonify(todo_item)


@app.route('/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    title = data.get('title')  # request.form['title']
    done = data.get('done')  # request.form['done']

    new_todo = Todo(title=title, done=done)
    db.session.add(new_todo)
    db.session.commit()

    return jsonify(new_todo), 201


@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo_item = Todo.query.filter_by(id=todo_id).first()
    if not todo_item:
        return jsonify({'message': 'No todo item found with id '
                        + str(todo_id)}), 404
    data = request.get_json()
    # update todo_item
    if data.get('title') is not None:
        todo_item.title = data.get('title')
    if data.get('done') is not None:
        todo_item.done = data.get('done')

    db.session.commit()

    return jsonify(todo_item)


@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo_item = Todo.query.filter_by(id=todo_id).first()
    if not todo_item:
        return jsonify({'message': 'No todo item found with id '
                        + str(todo_id)}), 404
    # remove todo_item from database
    db.session.delete(todo_item)
    db.session.commit()

    return jsonify({'message': 'Todo item deleted successfully'})


if __name__ == '__main__':
    app.run(debug=True)
