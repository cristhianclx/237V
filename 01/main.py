from flask import Flask, request


app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/hola")
def hello_friends():
    return "<p>Hello, friends!</p>"

@app.route("/messages")
def messages():
    return [{"name": "cristhian"}, {"name": "genaro"}]

@app.route("/user/<username>")
def user_username(username):
    print(username)
    return "Hello friend {}".format(username)

@app.route("/post/<int:post_id>")
def get_post_by_post_id(post_id):
    return "Post: {}".format(post_id)

data = [{
    "user": "cristhian",
    "password": 123456,
    "role": ["ADMIN", "NORMAL"]
}, {
    "user": "genaro",
    "password": 12345678,
    "role": ["NORMAL"]
}]

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data_input = request.get_json()
        # {'user': 'cristhian', 'password': '123456', 'role': 'ADMIN'}
        user = data_input.get("user")
        password = data_input.get("password")
        role = data_input.get("role")
        if user and password and role:
            for d in data:
                if user == d["user"] and password == str(d["password"]):
                    if role in d["role"]:
                        return {
                            "success": True,
                        }
                    else:
                        return {
                            "success": False,
                            "message": "role not allowed",
                        }
        return {
            "success": False,
            "message": "invalid credentials",
        }
    else:
        return {
            "success": False,
            "message": "you need to login",
        }