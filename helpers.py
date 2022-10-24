from curses.ascii import isalpha, islower, isupper
import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

# Insert google api here
api_key = "AIzaSyBgtSB8VJxzH1tpeFoN30zAgy7bm9NCMFM" 

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


def searchbook(name):
    """Look up quote for symbol."""

    # Contact with google book API
    try:
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
            eachbookinfo = getbookinfo(id, "s")
            bookinfo.append(eachbookinfo)
    
        return bookinfo
    except (KeyError, TypeError, ValueError):
        return None

# Have book id as a argument return dict with each book information
def getbookinfo(id, size):

    bookinfo = {}

    try:
        # Contact with api to get certain book information by ID
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
        if size == "s":
            bookinfo = {
                "id": id,
                "title": volumeInfo["title"],
                # "des": volumeInfo["description"],
                "smallthumb": volumeInfo["imageLinks"]["smallThumbnail"],
                # "thumb": volumeInfo["imageLinks"]["thumbnail"],
                # "smallpic": volumeInfo["imageLinks"]["small"],
                # "mediumpic": volumeInfo["imageLinks"]["medium"],
                # "largepic": volumeInfo["imageLinks"]["large"],
                # "moreinfo": volumeInfo["infoLink"],
                "authors": volumeInfo["authors"],
                # "cat": volumeInfo["mainCategory"]
            }
        # store full info into bookinfo dict
        elif size == "f":
            bookinfo = {
                "id": id,
                "title": volumeInfo["title"],
                "thumb": volumeInfo["imageLinks"]["thumbnail"],
                # "smallpic": volumeInfo["imageLinks"]["small"],
                # "mediumpic": volumeInfo["imageLinks"]["medium"],
                # "largepic": volumeInfo["imageLinks"]["large"],
                "moreinfo": volumeInfo["infoLink"],
                "authors": volumeInfo["authors"],
                "cat": volumeInfo["categories"],
                # "avgrate": volumeInfo["averageRating"],
                "pgcount": volumeInfo["pageCount"],
                "publisher": volumeInfo["publisher"]            
            }

        # Clear unuse html tag indescription
        re = ""
        remove = 1
        des = volumeInfo["description"]
        for c in range(len(des) - 1):
            
            if des[c] == "<" and remove == 1:
                remove *= -1
        
            if remove == 1:
                re += des[c]

            if des[c] == ">" and remove == -1:
                remove *= -1
            
            try:
                if des[c] == ">" and isalpha(des[c + 1]):
                    re += " "
            except IndexError:
                pass

        bookinfo["des"] = re
        try:
            bookinfo["avgrate"] = volumeInfo["averageRating"]
        except KeyError:
            pass
        
        return bookinfo
        
    except (KeyError, TypeError, ValueError):
         return "Key error"


