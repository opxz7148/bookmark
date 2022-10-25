
# pk_e4c2af32792443c9bbab8925cb105d41

from ast import Str, keyword
from lib2to3.pytree import generate_matches
from operator import ge, methodcaller
import os
from posixpath import split
import re
from tkinter import INSERT

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, getbookinfo, login_required, searchbook

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///book.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user = db.execute("SELECT * FROM bookusers WHERE id = ?", session["user_id"])


    return render_template("index.html", username=user[0]["username"])


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM bookusers WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # Get username from form
        username = request.form.get("username")

        # Check if username is exist
        if not username:
            return apology("Need username")

        password = request.form.get("password")

        # Check if password is exist
        if not password:
            return apology("Need password")

        # Check if password length are less then 8
        if len(password) < 8:
            return apology("Password need at least 8 characters")

        password_con = request.form.get("confirmation")

        # Check if password confirmation  is exist
        if not password_con:
            return apology("Please Confirm Your Password")

        # Check if password and password confirmation are match
        if password != password_con:
            return apology("Password confirmation doesn't match witn your password")

        hash_pass = generate_password_hash(password)

        # Get user favourite genre as list
        genres = request.form.getlist("genre")
        
        try:
            db.execute("INSERT INTO bookusers (username, hash) VALUES (?,?)", username, hash_pass)
        except ValueError:
            return apology("Username has been used")

        user_id = (db.execute("SELECT id FROM bookusers WHERE username = ?", username))[0]["id"]
        
        for genre in genres:
            genre_id = (db.execute("SELECT id FROM genre WHERE genre = ?", genre))[0]["id"]
            db.execute("INSERT INTO user_genre (userid, genreid) VALUES (?,?)", user_id, genre_id)
        return redirect("/login")

    # User call register page
    else:
        genres = db.execute("SELECT * FROM genre")
        app.logger.info(genres)
        return render_template("register.html", genres=genres)


@app.route("/search", methods=["GET", "POST"])
def search():
    
    # If recieve POST request 
    if request.method == "POST":
    
        # Get seacrh keyword
        keyword = request.form.get("booksearch")
        # Search key by ID
        book_re = searchbook(keyword)

        app.logger.info(book_re)


        # for book in book_re:
        #     app.logger.info(book)
        #     app.logger.info("")

        # Render template with book result and keyword
        return render_template("searchre.html", book_re=book_re, keyword=keyword)
    else:
        test = db.execute("SELECT * FROM bookusers WHERE id = 10")
        app.logger.info(test)
        return render_template("searchbook.html")


@app.route("/moreinfo", methods=["POST"])
def moreinfo():

    # If recieve POST request 
    if request.method == "POST":
        # Get book id from searh result page
        id = request.form.get("id")
        app.logger.info(id)

        # Get full information of certain book
        book = getbookinfo(id, "f")
        app.logger.info(book)

        check_collection = db.execute(
        """
        SELECT bookid 
        FROM users_book 
        WHERE userid = ? 
        AND 
        bookid = 
        (
            SELECT booknoid
            FROM book
            WHERE bookgid = ?
        )
        """
        , session["user_id"], id)
        
        if check_collection == []:
            incollection = False
        else:
            incollection = True

        # Render more info page with book information
        return render_template("moreinfo.html", book=book, incollection=incollection)


@app.route("/profile")
def profile():
    # Get user username
    username = (db.execute("SELECT username FROM bookusers WHERE id = ?", session["user_id"]))[0]["username"]
    
    # Get user fav genre
    usergenre = db.execute(
    """
    SELECT genre 
    FROM genre
    WHERE id IN
    (
        SELECT genreid 
        FROM user_genre
        WHERE userid = ?
    )
    """
    , session["user_id"])
    if usergenre == []:
        user_genre_c = False
    else:
        user_genre_c = True


    # Get user book ongoinng collection
    user_current = get_user_lst("O")
    if user_current == []:
        user_current_c = False
    else:
        user_current_c = True

    # Get user wishlist
    user_wish = get_user_lst("W")
    if user_wish == []:
        user_wish_c = False
    else:
        user_wish_c = True

    # Get user done list
    user_done = get_user_lst("D")
    if user_done == []:
        user_done_c = False
    else:
        user_done_c = True


    for book in user_current:
        book["authors"] = book["authors"].split(",")

    app.logger.info(user_genre_c)
    return render_template(
    "profile.html", 
    username=username, 
    usergenre=usergenre, 
    user_genre_c=user_genre_c,
    user_current=user_current,
    user_current_c=user_current_c, 
    user_wish=user_wish, 
    user_wish_c=user_wish_c,
    user_done=user_done, 
    user_done_c=user_done_c
    )


@app.route("/collection", methods=["POST"])
def add_to_collection():
    if request.method == "POST":
        # Get each information from form
        title = request.form.get("title")
        imglink = request.form.get("imglink")
        bookgid = request.form.get("id")
        authors = request.form.getlist("authors")
        # Combine all authors to one string
        seperator = ","
        authors = seperator.join(authors)

        try:
            db.execute(
            """
                INSERT INTO book
                (
                    bookgid,
                    imglink,
                    title,
                    authors
                )
                VALUES (?,?,?,?)
                """
            ,bookgid, imglink, title, authors)
        except ValueError:
            pass

        userid = session["user_id"]
        booknoid = (db.execute("SELECT booknoid FROM book WHERE bookgid = ?", bookgid))[0]["booknoid"]
    
        db.execute("INSERT INTO users_book (userid, bookid, status) VALUES(?,?,?)", userid, booknoid, "O")
    return redirect("/profile")


@app.route("/wish", methods=["POST"])
def add_to_wish():
    if request.method == "POST":
        # Get each information from form
        title = request.form.get("title")
        imglink = request.form.get("imglink")
        bookgid = request.form.get("id")
        authors = request.form.getlist("authors")
        # Combine all authors to one string
        seperator = ","
        authors = seperator.join(authors)

        try:
            db.execute(
            """
                INSERT INTO book
                (
                    bookgid,
                    imglink,
                    title,
                    authors
                )
                VALUES (?,?,?,?)
                """
            ,bookgid, imglink, title, authors)
        except ValueError:
            pass

        userid = session["user_id"]
        booknoid = (db.execute("SELECT booknoid FROM book WHERE bookgid = ?", bookgid))[0]["booknoid"]
    
        db.execute("INSERT INTO users_book (userid, bookid, status) VALUES(?,?,?)", userid, booknoid, "W")
    return redirect("/profile")


@app.route("/done", methods=["POST"])
def move_to_done():
    if request.method == "POST":
        booknoid = request.form.get("noid")
        app.logger.info(booknoid)
        db.execute('UPDATE users_book SET status = "D" WHERE userid = ? AND bookid = ?', session["user_id"], booknoid)
    return redirect("/profile")


@app.route("/gotit", methods=["POST"])
def move_to_ongoing():
    if request.method == "POST":
        booknoid = request.form.get("noid")
        app.logger.info(booknoid)
        db.execute('UPDATE users_book SET status = "O" WHERE userid = ? AND bookid = ?', session["user_id"], booknoid)
    return redirect("/profile")


@app.route("/remove", methods=["POST"])
def remove():
    if request.method == "POST":
        booknoid = request.form.get("noid")
        app.logger.info(booknoid)
        db.execute('DELETE FROM users_book WHERE userid = ? AND bookid = ?', session["user_id"], booknoid)
    return redirect("/profile")


def get_user_lst(type):

    if type != "W" and type != "O" and type != "D":
        return None
    user_lst = db.execute(
        """
        SELECT imglink, title, authors, bookgid, booknoid
        FROM book
        WHERE booknoid
        IN
        (
            SELECT bookid
            FROM users_book
            WHERE userid = ?
            AND 
            status = ?
        )
        """
    ,session["user_id"], type)
    
    return user_lst
    
