from flask import Flask, jsonify, request

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager


app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "Cibertec2024"

jwt = JWTManager(app)


# flask-migrate, sqlalchemy
# model User: username, password, name


users = [{
    "username": "cristhian",
    "password": "123456"
}, {
    "username": "genaro",
    "password": "654321"
}]


@app.route("/")
def home():
    return jsonify(working = True, version=1) # {"working": True}


@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None) # cristhian
    password = request.json.get("password", None) # 123456
    if username and password:
        for u in users:
            if u["username"] == username and u["password"] == password:
                access_token = create_access_token(identity=username)
                return jsonify(token=access_token)
        return jsonify({"msg": "Bad username or password"}), 401
    else:
        return jsonify({"msg": "Missing parameters"}), 401


@app.route("/me", methods=["GET"])
@jwt_required()
def me():
    current_user = get_jwt_identity()
    return jsonify(user_logged=current_user), 200


@app.route("/public", methods=["GET"])
def public():
    return jsonify(message="we don't need data"), 200


if __name__ == "__main__":
    app.run()


# Authorization: Bearer <access_token>