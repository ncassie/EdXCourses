import os

from flask import Flask, session, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

chatlist = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("test.html")

@app.route("/chats")
def chats():
    return render_template("chats.html")

@socketio.on("create chat")
def createchat(data):
    # get name of chatroom
    chatname = data["chatname"]

    # create a system user to provide welcome message
    user = "System"

    # generate first message
    message = "Welcome to the " + chatname + " chat."

    # create dictionary out of user and message
    messagedictionary = {"user": user, "message": message}

    # create list of messages for chat room
    messagelist = [messagedictionary]

    # add chatroom and associated message to chatlist
    chatlist[chatname] = messagelist

    emit("chat created", {"chatname": chatname}, broadcast=True)

@app.route("/processlogin", methods=["POST", "GET"])
def processlogin():
    username = request.form.get("username")
    return render_template("chats.html", message=username, chats=chatlist)
