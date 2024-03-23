from flask import Flask, request, jsonify
from flask_caching import Cache
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
import redis
import json


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

config = {
    "DEBUG": True,
    "CACHE_TYPE": "redis",
    "CACHE_REDIS_HOST": "localhost",
    "CACHE_REDIS_PORT": 6379,
    "CACHE_REDIS_DB": 0,
    "CACHE_DEFAULT_TIMEOUT": 300
}
app.config.from_mapping(config)

cache = Cache(app)

redis_client = redis.Redis(host="localhost", port=6379, db=0)

ma = Marshmallow(app)

db = SQLAlchemy(app)
app.debug = True

migrate = Migrate(app, db)

api = Api(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    age = db.Column(db.Integer, nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<User {self.id}>"


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", backref="user")

    def __repr__(self):
        return f"<Message {self.id}>"


class UserBasicSchema(ma.Schema):
    class Meta:
        fields = ("id", "name")
        model = User


users_basic_schema = UserBasicSchema(many = True)


class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "age", "created_at")
        model = User
        datetimeformat = "%Y-%m-%d %H:%M"


user_schema = UserSchema()
users_schema = UserSchema(many = True)


class MessageSchema(ma.Schema):
    user = ma.Nested(UserSchema)

    class Meta:
        fields = ("id", "content", "created_at", "user")
        model = Message
        datetimeformat = "%Y-%m-%d %H:%M"


message_schema = MessageSchema()
messages_schema = MessageSchema(many = True)


class WorkingResource(Resource):
    def get(self):
        return {"working": True}
    

class PublicUserResource(Resource):
    def get(self): # return all users
        users_data = User.query.all()
        users_results = users_basic_schema.dump(users_data)
        return users_results


class UserResource(Resource):
    def get(self): # return all users
        users_data = User.query.all()
        users_results = users_schema.dump(users_data)
        cached_response = redis_client.get("users")
        if cached_response:
            return json.loads(str(cached_response.decode()).replace("'", '"'))
        else:
            redis_client.set("users", str(users_results))
            return users_results
    
    def post(self): # create new user
        data_user = request.get_json()
        # {'name': 'raul', 'age': 32, 'id': 1}
        # user = User(name=data_user["name"], age=data_user["age"])
        user = User(**data_user)
        db.session.add(user)
        db.session.commit()
        cache.delete("users")
        return user_schema.dump(user), 201
    

class UserByIDResource(Resource):
    def get(self, id):
        user = User.query.filter_by(id = id).first()
        if user is None:
            return {}, 404 # not found
        return user_schema.dump(user)
    
    def put(self, id):
        user = User.query.filter_by(id = id).first()
        if user is None:
            return {}, 404 # not found
        data_user = request.get_json()
        if "name" in data_user and "age" in data_user:
            user.name = data_user["name"]
            user.age = data_user["age"]
            db.session.add(user)
            db.session.commit()
            return user_schema.dump(user)
        else:
            return {}, 400
    
    def patch(self, id):
        user = User.query.filter_by(id = id).first()
        if user is None:
            return {}, 404 # not found
        data_user = request.get_json()
        if "name" in data_user:
            user.name = data_user["name"]
        if "age" in data_user:
            user.age = data_user["age"]
        db.session.add(user)
        db.session.commit()
        return user_schema.dump(user)
    
    def delete(self, id):
        user = User.query.filter_by(id = id).first()
        if user is None:
            return {}, 404 # not found
        db.session.delete(user)
        db.session.commit()
        return {}, 204


class MessageResource(Resource):
    def get(self): # return all messages
        messages_data = Message.query.all()
        messages_results = messages_schema.dump(messages_data)
        return messages_results    


class MessagesByUserResource(Resource):
    def get(self, user_id):
        user = User.query.filter_by(id = user_id).first()
        if user is None:
            return {}, 404 # not found
        messages_data = Message.query.filter_by(user_id = user_id).all()
        messages_results = messages_schema.dump(messages_data)
        return messages_results
    
    def post(self, user_id): # create a new message
        user = User.query.filter_by(id = user_id).first()
        if user is None:
            return {}, 404 # not found
        data_message = request.get_json()
        message = Message(**data_message)
        message.user = user
        db.session.add(message)
        db.session.commit()
        return message_schema.dump(message), 201


class MessageByIDResource(Resource):
    def get(self, id):
        message = Message.query.filter_by(id = id).first()
        if message is None:
            return {}, 404 # not found
        return message_schema.dump(message)

    def patch(self, id):
        message = Message.query.filter_by(id = id).first()
        if message is None:
            return {}, 404 # not found
        data_message = request.get_json()
        if "content" in data_message:
            message.content = data_message["content"]
        db.session.add(message)
        db.session.commit()
        return message_schema.dump(message)
    
    def delete(self, id):
        message = Message.query.filter_by(id = id).first()
        if message is None:
            return {}, 404 # not found
        db.session.delete(message)
        db.session.commit()
        return {}, 204


api.add_resource(WorkingResource, "/")
api.add_resource(PublicUserResource, "/public/users")
api.add_resource(UserResource, "/users")
api.add_resource(UserByIDResource, "/users/<int:id>")
api.add_resource(MessagesByUserResource, "/messages-by-user/<int:user_id>")
api.add_resource(MessageResource, "/messages")
api.add_resource(MessageByIDResource, "/messages/<int:id>")


@app.route("/data", methods=["GET"])
@cache.cached(timeout = 60)
def data():
    return [{ "id": "1", "name": "cristhian"}, { "id": "2", "name": "genaro" }]


# app.route("/users-all") cache timeout = 3600
# todos los users

# invalide la cache: borras un usuario, editas un usuario o agregas un usuario


if __name__ == "__main__":
    app.run(debug=True)