
# pk_e4c2af32792443c9bbab8925cb105d41

from ast import keyword
import os
import re

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, getbookinfo, login_required, searchbook, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


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
    user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])


    return render_template("index.html", username=user[0]["username"], cash=usd(user[0]["cash"]), usd=usd)


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
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

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

        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?,?)", username, hash_pass)
        except ValueError:
            return apology("Username has been used")

        return redirect("/login")

    # User call register page
    else:
        return render_template("register.html")


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "POST":
        keyword = request.form.get("booksearch")
        book_re = searchbook(keyword)
        app.logger.info(book_re)

        for book in book_re:
            app.logger.info(book)
            app.logger.info("")

        return render_template("searchre.html", book_re=book_re, keyword=keyword)
    else:
        return render_template("searchbook.html")

@app.route("/moreinfo", methods=["POST"])
@login_required
def moreinfo():
    if request.method == "POST":
        id = request.form.get("id")
        book = getbookinfo(id, "f")
        app.logger.info(book)
        return render_template("moreinfo.html", book=book)

