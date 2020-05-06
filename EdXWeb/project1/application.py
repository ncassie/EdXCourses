import os
import requests

from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

KEY="PulW6whnNMTYnsbzDzUzA"


# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    if session.get("user_id") is None:
        return render_template("login.html")
    return render_template("search.html")

@app.route("/logout")
def logout():
    session["user_id"] = None
    return render_template("login.html", message="Thank you for visiting.  Please stop by again!")

# this method handles the form submission from the login page
@app.route("/processlogin", methods=["POST"])
def processlogin():

    # Get form information.
    username = request.form.get("username")
    password = request.form.get("password")

    # Make sure username not already in database.
    if db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": username, "password": password}).rowcount == 0:
        return render_template("login.html", message="Log in Incorrect. Please Try Again.")
    user = db.execute("SELECT id FROM users WHERE username = :username AND password = :password", {"username": username, "password": password}).fetchone()
    session["user_id"] = user.id
    return render_template("search.html")


# signup presents the form for a user to sign up for sanitize
@app.route("/signup")
def signup():
    return render_template("signup.html")

# registered provides functionality to recieve signup information from form
# and register it in database
@app.route("/registered", methods=["POST"])
def registered():
    """Register A New User."""

    # Get form information.
    username = request.form.get("username")
    password = request.form.get("password")

    # Make sure username not already in database.
    if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount != 0:
        return render_template("signup.html", message="That username is already taken.  Please try another one.")
    db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
            {"username": username, "password": password})
    db.commit()
    user = db.execute("SELECT id FROM users WHERE username = :username AND password = :password", {"username": username, "password": password}).fetchone()
    session["user_id"] = user.id
    return render_template("search.html")

#search.html presents search page to user
@app.route("/search")
def search():
    if session.get("user_id") is None:
        return render_template("login.html", message="Please log in to search.")
    return render_template("search.html")

#displays search results to user
@app.route("/searchresults", methods=["POST"])
def searchresults():
    if session.get("user_id") is None:
        return render_template("login.html", message="Please log in to search.")

    # Get form information.
    searchby = request.form.get("searchby")
    criteria = request.form.get("criteria")

    # perform appropriate search
    if searchby == "author":
        books = db.execute("SELECT * FROM books WHERE author LIKE :criteria", {"criteria": '%' + criteria + '%'}).fetchall()
    elif searchby == "title":
        books = db.execute("SELECT * FROM books WHERE title LIKE :criteria", {"criteria": '%' + criteria + '%'}).fetchall()
    else:
        books = db.execute("SELECT * FROM books WHERE isbn LIKE :criteria", {"criteria": '%' + criteria + '%'}).fetchall()
    return render_template("books.html", books=books)

# displays informaiton on selected book
@app.route("/books/<int:book_id>")
def book(book_id):
    """Lists details about a single book."""

    if session.get("user_id") is None:
        return render_template("login.html", message="Please log in to view book information")

    # Make sure book exists.
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    if book is None:
        return render_template("search.html", message="Sorry, we couldn't find that book.")

    # get review information from database
    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": book_id}).fetchall()

    # got book information from Goodreads
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": KEY, "isbns": book.isbn, "format": "json"})

    # take result from request and extract as json
    data = res.json()

    # parse book object from json
    data = data['books'][0]

    # parse average rating and number of ratings from json object
    averageRating = data['average_rating']
    numRatings = data['ratings_count']

    return render_template("book.html", book=book, reviews=reviews, averageRating=averageRating, numRatings=numRatings)

# process form submission from book page for  book review
# returns user back to book they just left review for
@app.route("/reviewsubmitted", methods=["Post"])
def reviewsubmitted():

    if session.get("user_id") is None:
        return render_template("login.html", message="Please log in to leave a review")

    # Get form information.
    userId = session.get("user_id")
    bookId = request.form.get("bookId")
    reviewText = request.form.get("reviewText")
    rating = request.form.get("rating")

    # if user already submitted a review, return them to the book page
    if db.execute("SELECT * FROM reviews WHERE book_id = :book_id AND user_id = :user_id", {"book_id": bookId, "user_id": userId}).rowcount != 0:
        return book(bookId)

    # insert review into database
    db.execute("INSERT INTO reviews (user_id, book_id, review_text, rating) VALUES (:userId, :bookId, :reviewText, :rating)",
            {"userId": userId, "bookId": bookId, "reviewText": reviewText, "rating": rating})
    db.commit()

    return book(bookId)

# generate json for api allowing book information pull based on isbn
@app.route("/api/<string:isbn>")
def api(isbn):
    #  book’s title, author, publication date, ISBN number, review count, and average score
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book == None:
        return jsonify({"error": "Invalid ISBN"}), 404

    review_count = db.execute("SELECT * FROM reviews WHERE book_id = :book_id", {"book_id": book.id}).rowcount
    average_rating = db.execute("SELECT AVG(rating) FROM reviews WHERE book_id = :book_id", {"book_id": book.id}).fetchone()
    return   jsonify({
            "title": book.title,
            "author": book.author,
            "publication_date": book.publication_year,
            "isbn": book.isbn,
            "review_count": review_count,
            "average_rating": average_rating.avg
        })
