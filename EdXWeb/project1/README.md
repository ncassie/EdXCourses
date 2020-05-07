# Project 1

Web Programming with Python and JavaScript

This is my implementation of the book review website using flask and raw sql.

application.py contains all of the python code for this project with the appropriate routing.

import.py was used to import the data from the provided csv to my database.  My database has 3 tables as follows:

books:
  id	integer SERIAL
  isbn	VARCHAR NOT NULL
  title	VARCHAR NOT NULL
  author	VARCHAR	 NOT NULL
  publication_year	Integer

reviews
  id	integer SERIAL
  user_id	integer NOT NULL REFERENCES users
  book_id	integer NOT NULL	REFERENCES books
  review_text	VARCHAR
  rating	INTEGER

users
  id	INTEGER SERIAL
  username	VARCHAR
  password	VARCHAR

The html files contain the following:
  layout.html provides the template layout for pages when a user is not logged in
  loginlayout.html provides the template layout for pages when a user is logged in and contains a navbar
  login.html - contains a form that allows the user to login
  signup.html - cotains the form that allows the user to registers to use the site
  search.html - contains the search form to allow users to search by isbn, title, author
  books.html - lists all of the results from a user's searching
  book.html - provides details for the specified book.
