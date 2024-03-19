from flask import Flask, request
from flask_restful_swagger_3 import Api, Resource, swagger
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

db = SQLAlchemy(app)
app.debug = True

migrate = Migrate(app, db)

api = Api(app, swagger_prefix_url="/docs")


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<User {self.id}>"


class WorkingResource(Resource):
    def get(self):
        return {"working": True}
    

class UserResource(Resource):
    @swagger.tags(['users'])
    def get(self): # return all users
        users_data = User.query.all()
        users_results = []
        for user_data in users_data:
            users_results.append({
                "id": user_data.id,
                "name": user_data.name,
                "age": user_data.age,
                "created_at": user_data.created_at.strftime("%Y-%m-%d %H:%M")
            })
        return users_results
    
    def post(self): # create new user
        data_user = request.get_json()
        # {'name': 'raul', 'age': 32, 'id': 1}
        # user = User(name=data_user["name"], age=data_user["age"])
        user = User(**data_user)
        db.session.add(user)
        db.session.commit()
        return {
            "id": user.id,
            "name": user.name,
            "age": user.age,
            "created_at": user.created_at.strftime("%Y-%m-%d %H:%M")
        }, 201
    

class UserByIDResource(Resource):
    def get(self, id):
        user = User.query.filter_by(id = id).first()
        if user is None:
            return {}, 404 # not found
        return {
            "id": user.id,
            "name": user.name,
            "age": user.age,
            "created_at": user.created_at.strftime("%Y-%m-%d %H:%M")
        }
    
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
            return {
                "id": user.id,
                "name": user.name,
                "age": user.age,
                "created_at": user.created_at.strftime("%Y-%m-%d %H:%M")
            }
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
        return {
            "id": user.id,
            "name": user.name,
            "age": user.age,
            "created_at": user.created_at.strftime("%Y-%m-%d %H:%M")
        }
    
    def delete(self, id):
        user = User.query.filter_by(id = id).first()
        if user is None:
            return {}, 404 # not found
        db.session.delete(user)
        db.session.commit()
        return {}, 204


api.add_resource(WorkingResource, "/")
api.add_resource(UserResource, "/users")
api.add_resource(UserByIDResource, "/users/<int:id>")


if __name__ == "__main__":
    app.run(debug=True)