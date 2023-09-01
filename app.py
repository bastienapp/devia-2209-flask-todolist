from dataclasses import dataclass
import datetime
from flask import Flask, abort, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import jwt
app = Flask(__name__)

secret_key = 'secretsecretsecretsecretsecret'
#  app.config['SECRET_KEY'] = 'secretsecretsecretsecretsecret'

ROLE_ADMIN = 1
ROLE_USER = 2

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
    user_id: int

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    done = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


@dataclass
class User(db.Model):
    id: int
    email: str

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'),
                        nullable=False)


@dataclass
class Role(db.Model):
    id: int
    name: str

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)


@app.route('/create-db')
def create_db():
    with app.app_context():
        db.drop_all()
        db.create_all()

        role_admin = Role(name='admin')
        db.session.add(role_admin)
        role_user = Role(name='user')
        db.session.add(role_user)

        admin = User(email='admin@simplon.co',
                     password=bcrypt.generate_password_hash('admin')
                     .decode('utf-8'), role_id=ROLE_ADMIN)
        db.session.add(admin)

        db.session.commit()
    return 'create db'


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # find user with email
    user = User.query.filter_by(email=email).first()
    if user is None:
        abort(401)
    if bcrypt.check_password_hash(user.password, password):

        encoded = jwt.encode(
            {
                'user_id': user.id,
                'email': user.email,
                'iat':  datetime.datetime.utcnow(),
                'exp': datetime.datetime.utcnow()
                + datetime.timedelta(minutes=30)
            },
            secret_key,
            "HS256"
        )

        return jsonify({'token': encoded})
    else:
        abort(401)


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    #  hash password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    new_user = User(email=email, password=hashed_password, role_id=ROLE_USER)
    db.session.add(new_user)
    db.session.commit()

    # todo try except for duplicate email

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


def jwt_required():
    # check jwt : user needs to be logged in
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        abort(403)
    token = auth_header.split(' ')[1]  # "Bearer <token>"
    if token is None:
        abort(403)
    try:
        jwt_decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
        # retrieve user from database with email
        user = User.query.filter_by(email=jwt_decoded['email']).first()
        if user is None:
            abort(403)
        return user
    except jwt.exceptions.DecodeError:
        abort(403)


@app.route('/todos', methods=['POST'])
def create_todo():
    current_user = jwt_required()

    # here user is logged in
    data = request.get_json()
    title = data.get('title')  # request.form['title']
    done = data.get('done')  # request.form['done']

    new_todo = Todo(title=title, done=done, user_id=current_user.id)
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
    current_user = jwt_required()

    if current_user.role_id != ROLE_ADMIN:
        abort(403)

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
