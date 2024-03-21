from flask import Flask, jsonify, request

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SECRET_KEY"] = "Cibertec2024"
app.config["JWT_SECRET_KEY"] = "Cibertec2024"
app.debug = True

db = SQLAlchemy(app)

migrate = Migrate(app, db)

jwt = JWTManager(app)


class User(db.Model):
    username = db.Column(db.String(150), primary_key=True)
    password = db.Column(db.String(150), nullable=False) # passwords needs to be encrypted
    name = db.Column(db.String(150), nullable=False)

# name # borrar
# first_name
# last_name
# age
# role # ADMIN, NORMAL

    def check_password(self, password):
        if self.password == password:
            return True
        else:
            return False
        
    def __repr__(self):
        return "<User {}>".format(self.username)


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


@app.route("/me", methods=["GET"])
@jwt_required()
def me():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username = current_user).one_or_none()
    return jsonify(name = user.name), 200


# /me funcione para todos los usuarios autenticados ADMIN, NORMAL, ahora devuelva mas datos
# /reports funcione solo para los usuarios ADMIN


@app.route("/public", methods=["GET"])
def public():
    return jsonify(message="we don't need data"), 200


if __name__ == "__main__":
    app.run()


# Authorization: Bearer <access_token>