from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Cibertec2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.debug = True

db = SQLAlchemy(app)

migrate = Migrate(app, db)

ma = Marshmallow(app)

socketio = SocketIO(app)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(150), nullable=False)
    to = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return "<Message {}>".format(self.id)


class MessageSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "to", "message", "created_at")
        model = Message
        datetimeformat="%Y-%m-%d %H:%M"


message_schema = MessageSchema()
messages_schema = MessageSchema(many = True)


@app.route("/")
def home():
    messages_data = Message.query.all()
    messages_results = messages_schema.dump(messages_data)
    return render_template("home.html", messages=messages_results)


@socketio.on("messages")
def messages(data, methods=["GET", "POST"]):
    # {'username': 'cristhian', 'message': '123456'}
    data["to"] = "ALL"
    message = Message(**data)
    db.session.add(message)
    db.session.commit()
    socketio.emit("messages-response", message_schema.dump(message))


@socketio.on("directs")
def directs(data, methods=["GET", "POST"]):
    message = Message(**data)
    db.session.add(message)
    db.session.commit()
    socketio.emit("directs-response", message_schema.dump(message))



if __name__ == '__main__':
    socketio.run(app)