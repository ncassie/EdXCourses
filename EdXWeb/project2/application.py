import os

from flask import Flask, session, render_template, request, jsonify
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

    print(chatlist[chatname])
    emit("chat created", {"chatname": chatname}, broadcast=True)

@socketio.on("submit message")
def submitmessage(data):
    #get name of message sender
    messagesender = data["user"]
    print(messagesender)
    
    #get chat room message was sent in
    room = data["room"]

    #get message
    message = data["message"]

    # create dictionary out of user and message
    messagedictionary = {"user": messagesender, "message": message}

    # get message list for chat room
    messagelist = chatlist[room]

    messagelist.append(messagedictionary)

    # add updaed message list back to dictionary
    chatlist[room] = messagelist
    print(chatlist[room])
    emit("message received", {"user": messagesender, "room": room, "message": message}, broadcast=True)

@app.route("/loadchat", methods=["POST"])
def loadchat():
    chatroom = request.form.get("chatname")
    print("Chatroom " + chatroom)

    messages = chatlist[chatroom]
    print(messages)

    return jsonify({"messages": messages})


@app.route("/chats", methods=["POST", "GET"])
def chats():
    username = request.form.get("username")
    return render_template("chats.html", message=username, chats=chatlist)
