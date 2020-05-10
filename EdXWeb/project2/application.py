import os

from flask import Flask, session, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("test.html")

@app.route("/chats")
def chats():
    return render_template("chats.html")

@socketio.on("submit vote")
def vote(data):
    selection = data["selection"]
    return render_template("chats.html")

@app.route("/processlogin", methods=["POST"])
def processlogin():

    username = request.form.get("username")
    return render_template("chats.html", message=username)
