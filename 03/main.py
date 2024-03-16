from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.sql import func


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/acerca-de")
def about_us():
    return render_template("about-us.html")