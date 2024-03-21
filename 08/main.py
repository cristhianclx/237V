from functools import wraps

from flask import Flask, jsonify, request

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import get_jwt


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SECRET_KEY"] = "Cibertec2024"
app.config["JWT_SECRET_KEY"] = "Cibertec2024"
app.debug = True

ma = Marshmallow(app)

db = SQLAlchemy(app)

migrate = Migrate(app, db)

jwt = JWTManager(app)


USER_ROLE_ADMIN = "ADMIN"
USER_ROLE_NORMAL = "NORMAL"

class User(db.Model):
    username = db.Column(db.String(150), primary_key=True)
    password = db.Column(db.String(150), nullable=False) # passwords needs to be encrypted
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    role = db.Column(db.String(30), nullable=False) # ADMIN, NORMAL

    def check_password(self, password):
        if self.password == password:
            return True
        else:
            return False
        
    def __repr__(self):
        return "<User {}>".format(self.username)


class UserSchema(ma.Schema):
    class Meta:
        fields = ("username", "first_name", "last_name", "age", "role")
        model = User


user_schema = UserSchema()


def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            data_in_jwt = get_jwt()
            current_user = data_in_jwt["sub"]
            user = User.query.filter_by(username = current_user).one_or_none()
            if user and user.role == USER_ROLE_ADMIN:
                return fn(*args, **kwargs)
            else:
                return jsonify(msg="Admins only"), 403
        return decorator
    return wrapper


def is_admin_or_is_normal():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            data_in_jwt = get_jwt()
            current_user = data_in_jwt["sub"]
            user = User.query.filter_by(username = current_user).one_or_none()
            if user and (user.role == USER_ROLE_ADMIN or user.role == USER_ROLE_NORMAL):
                return fn(*args, **kwargs)
            else:
                return jsonify(msg="Members only"), 403
        return decorator
    return wrapper


@app.route("/")
def home():
    return jsonify(working = True, version=1) # {"working": True}


@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None) # cristhian
    password = request.json.get("password", None) # 123456
    if username and password:
        user = User.query.filter_by(username = username).one_or_none()
        if user and user.check_password(password):
            access_token = create_access_token(identity=username)
            return jsonify(token=access_token)
        return jsonify({"msg": "Bad username or password"}), 401
    else:
        return jsonify({"msg": "Missing parameters"}), 401


@app.route("/me-old", methods=["GET"])
@jwt_required()
def me_old():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username = current_user).one_or_none()
    return user_schema.dump(user)
    

@app.route("/me", methods=["GET"])
@is_admin_or_is_normal()
def me():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username = current_user).one_or_none()
    return user_schema.dump(user)


@app.route("/reports", methods=["GET"])
@admin_required()
def reports():
    return {"reports": [1, 2, 3, 4, 5]}


@app.route("/public", methods=["GET"])
def public():
    return jsonify(message="we don't need data"), 200


if __name__ == "__main__":
    app.run()


# Authorization: Bearer <access_token>