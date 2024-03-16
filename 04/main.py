from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.sql import func


app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@host:port/database_name'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@host:port/database_name'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:sistemas@127.0.0.1:5432/cibertec'

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(200))
    last_name = db.Column(db.String(200))
    age = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())


@app.route("/users")
def users():
    users_data = User.query.all()
    return render_template("users.html", users=users_data)


@app.route("/users/<int:id>")
def users_by_id(id):
    user = User.query.get_or_404(id)
    return render_template("user.html", user=user)


@app.route("/users/add", methods=["GET", "POST"])
def users_add():
    if request.method == "GET":
        return render_template("users-add.html")
    if request.method == "POST":
        import ipdb; ipdb.set_trace()
        
    