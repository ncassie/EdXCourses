import os

from flask import Flask, session, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

chatlist = {}

@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("create chat")
def createchat(data):
    # get name of chatroom
    chatname = data["chatname"]

    if(chatname not in chatlist):

        # create a system user to provide welcome message
        user = "System - " + datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")

        # generate first message
        message = "Welcome to the " + chatname + " chat."

        # create dictionary out of user and message
        messagedictionary = {"user": user, "message": message}

        # create list of messages for chat room
        messagelist = [messagedictionary]

        # add chatroom and associated message to chatlist
        chatlist[chatname] = messagelist

        success = True
    else:
        success = False
    emit("chat created", {"success": success, "chatname": chatname}, broadcast=True)

#loads messages for selected chatroom
@app.route("/loadchat", methods=["POST"])
def loadchat():

    # get desired chatroom from input
    chatroom = request.form.get("chatname")

    #load messages for selected chatroom
    messages = chatlist[chatroom]

    # return json object containing all messages for chatroom
    return jsonify({"messages": messages})

# route for channel page
@app.route("/chats", methods=["POST", "GET"])
def chats():
    username = request.form.get("username")
    return render_template("chats.html", message=username, chats=chatlist)

# Process and transmit public message
@socketio.on("submit message")
def submitmessage(data):
    #get name of message sender
    messagesender = data["user"]

    #add datestamp to user
    messagesender = messagesender + " - " + datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")

    #get chat room message was sent in
    room = data["room"]

    #get message
    message = data["message"]

    # create dictionary out of user and message
    messagedictionary = {"user": messagesender, "message": message}

    # get message list for chat room
    messagelist = chatlist[room]

    #Ensure size of message list remains at or below 100
    if len(messagelist) > 100:
        messagelist.pop(0)

    # add new message to message list
    messagelist.append(messagedictionary)

    # add updaed message list back to dictionary
    chatlist[room] = messagelist

    emit("message received", {"user": messagesender, "room": room, "message": message}, broadcast=True)

# handles sending of private message
@socketio.on("submit private message")
def submitprivatemessage(data):

    # load specified input
    recevier = data["receiver"]
    sender = data["user"]
    message = data["message"]

    # construct private message to send
    message = sender + " says " + message

    # emit private message and recipient
    emit("private message received", {"receiver": recevier, "message": message}, broadcast=True)
