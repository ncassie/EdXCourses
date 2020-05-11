import os

from flask import Flask, session, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

chatlist = []

@app.route("/")
def index():
    print("This is a test")
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("test.html")

@app.route("/chats")
def chats():
    return render_template("chats.html")

@socketio.on("create chat")
def createchat(data):
    print("We got to the createchat method")
    chatname = data["chatname"]
    chatlist.append(chatname)
    emit("chat created", {"chatname": chatname}, broadcast=True)

@app.route("/processlogin", methods=["POST", "GET"])
def processlogin():
    username = request.form.get("username")
    return render_template("chats.html", message=username, chats=chatlist)
