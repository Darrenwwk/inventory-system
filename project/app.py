import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

from helpers import apology, login_required, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

# Make sure API key is set
#if not os.environ.get("API_KEY"):
 #   raise RuntimeError("API_KEY not set")


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
    user_id = session["user_id"]

    alldb = db.execute("SELECT name, quantity, created_at, updated_at FROM inventory WHERE user_id = (?)", user_id)

    return render_template("main.html", dbs = alldb)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """Add item"""
    if request.method == "GET":
        return render_template("add.html")

    else:
        product_name = request.form.get("productname")
        quantity = request.form.get("quantity")

        if not product_name:
            return apology("Product name is missing!")

        if not quantity:
            return apology("Invalid quantity!")

        user_id = session["user_id"]

        date = datetime.datetime.now()

        test = db.execute("SELECT name FROM inventory WHERE name = (?) AND user_id = (?)", product_name, user_id)

        if len(test) > 0:
            return apology("Item is already exists!")

        db.execute("INSERT INTO inventory (name, quantity, created_at, user_id) VALUES (?, ?, ?, ?)", product_name, quantity, date, user_id)

        flash("Added!")

        return redirect("/")


@app.route("/reset_password", methods=["GET", "POST"])
@login_required
def reset():
    """Reset the password"""
    if request.method == "GET":
        return render_template("reset.html")
    else:
        new_pass = request.form.get("reset")

        if not new_pass:
            return apology("Opps! New password is missing")

        hash_newpass = generate_password_hash(new_pass)

        user_id = session["user_id"]

        db.execute("UPDATE users SET hash = (?) WHERE id = (?)", hash_newpass, user_id)

        flash("Password reset successful!")

        return redirect("/")


@app.route("/remove", methods=["GET", "POST"])
@login_required
def history():
    """remove item"""
    if request.method == "GET":
        user_id = session["user_id"]
        products = db.execute("SELECT name , id FROM inventory WHERE user_id = (?)", user_id)
        return render_template("remove.html", products=products)

    else:
        product_id = request.form.get("product")

        if not product_id:
            return apology("Product is missing!")

        user_id = session["user_id"]

        db.execute("DELETE FROM inventory WHERE id = (?)", product_id)

        flash(f"Item {product_id} has been deleted!")

        return redirect("/")


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

        username = rows[0]["username"]

        flash(f"Welcome,{username}!")

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


@app.route("/search", methods=["GET", "POST"])
@login_required
def quote():
    """search product"""
    if request.method == "GET":
        return render_template("search.html")
    else:
        search_product = request.form.get("search")

        if not search_product:
            return apology("Product is missing")

        user_id = session["user_id"]

        product_db = db.execute("SELECT name, quantity, updated_at FROM inventory WHERE name = (?) AND user_id = (?)", search_product, user_id)

        if not product_db:
            return apology("Invalid item")

    return render_template("searched.html", products=product_db)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")

    else:  # POST method will execute below code
        username = request.form.get("username")  # to grab data from user inputs
        password = request.form.get("password")
        confirm_password = request.form.get("confirmation")

        # do some validation
        if not username:
            return apology("Opps! Username is missing")

        if not password:
            return apology("Opps! Password is missing")

        if not confirm_password:
            return apology("Opps! Confirm password is missing")

        # if confirm password do no match with password
        if password != confirm_password:
            return apology("Opps! Confirm password is not match")

        # encript the confirm password with hash function
        hash_pass = generate_password_hash(confirm_password)

        try:  # insert data into database
            user = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash_pass)
        except:
            return apology("Username is exist")

        session["user_id"] = user

        return redirect("/")


@app.route("/edit", methods=["GET", "POST"])
@login_required
def sell():
    """edit product"""
    if request.method == "GET":
        user_id = session["user_id"]
        products = db.execute("SELECT name , id FROM inventory WHERE user_id = (?)", user_id)
        return render_template("edit.html", products=products)
    else:
        product_id= request.form.get("product")
        quantity = request.form.get("quantity")

        if not product_id:
            return apology("product is missing")

        if not quantity:
            return apology("quantity is missing")

        date = datetime.datetime.now()

        db.execute("UPDATE inventory SET quantity = (?), updated_at = (?) WHERE id = (?)", quantity, date, product_id)

        flash("Item has been updated!")

        return redirect("/")
