from flask import Flask, render_template, request, redirect
from werkzeug.security import generate_password_hash
from helpers import db  # assuming helpers.py has your db connection

app = Flask(__name__)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # basic validation
        if not username or not password or not confirmation:
            return "Missing username or password", 400
        if password != confirmation:
            return "Passwords do not match", 400

        # check if username already exists
        existing = db.execute("SELECT * FROM users WHERE username = ?", username)
        if existing:
            return "Username already exists", 400

        # hash the password
        hash_pw = generate_password_hash(password)

        # insert new user
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash_pw)

        # redirect to login
        return redirect("/login")

    else:
        return render_template("register.html")
