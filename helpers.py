import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        url = f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None

def searchbook(name):
    """Look up quote for symbol."""

    # Contact with google book API
    try:
        api_key = os.environ.get("API_KEY")
        url = f"https://www.googleapis.com/books/v1/volumes?q={name}&maxResults=10&key={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        bookRe = response.json()
        
        # Create list to store book id
        id_list = []

        # Store each book id into id_list
        for book in bookRe["items"]:
            id_list.append(book["id"])
        
        # Create list to store every book info
        bookinfo = []

        for id in id_list:
            eachbookinfo = getbookinfo(id)
            bookinfo.append(eachbookinfo)
    
        return bookinfo
    except (KeyError, TypeError, ValueError):
        return None

# Have book id as a argument return dict with each book information
def getbookinfo(id):

    bookinfo = {}

    try:
        api_key = os.environ.get("API_KEY")
        url = f"https://www.googleapis.com/books/v1/volumes/{id}?key={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        bookRe = response.json()
        volumeInfo = bookRe["volumeInfo"]
        bookinfo = {}
         # store nescessary info into bookinfo dict
        bookinfo = {
            "id": id,
            "title": volumeInfo["title"],
            "des": volumeInfo["description"],
            "smallpic": volumeInfo["imageLinks"]["small"],
            "mediumpic": volumeInfo["imageLinks"]["medium"],
            "largepic": volumeInfo["imageLinks"]["large"],
            "moreinfo": volumeInfo["infoLink"],
            "smallthumb": volumeInfo["imageLinks"]["smallThumbnail"]
        }

        # If there only one author directly add into dict 
        if len(volumeInfo["authors"]) < 2:
            bookinfo["authors"] = volumeInfo["authors"][0]
        # If there more then one author combine each into string and add into dict
        else:
            authors = ""
            for author in volumeInfo["authors"]:
                authors += ", " + author   
            bookinfo["authors"] = authors

        return bookinfo
        
    except (KeyError, TypeError, ValueError):
        return None



def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

# def getimglink(bookinfo, size=0):
#     if size == 0:
#         return bookinfo["smallpic"]
#     else:
#         return bookinfo["medium"]
