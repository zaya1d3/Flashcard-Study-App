from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import db

app = Flask(__name__)
app.secret_key = "supersecretkey"  # change this in production

# --------------------
# ROUTES
# --------------------

@app.route("/")
def index():
    # check if logged in
    if "user_id" not in session:
        return redirect("/login")

    # show user's flashcards
    rows = db.execute("SELECT * FROM flashcards WHERE user_id = ?", session["user_id"])
    return render_template("index.html", cards=rows)


# --------------------
# REGISTER
# --------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation:
            flash("Missing fields")
            return redirect("/register")

        if password != confirmation:
            flash("Passwords do not match")
            return redirect("/register")

        # check if username exists
        existing = db.execute("SELECT * FROM users WHERE username = ?", username)
        if existing:
            flash("Username already exists")
            return redirect("/register")

        # insert user
        hash_pw = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash_pw)
        flash("Registered successfully. Please log in.")
        return redirect("/login")

    return render_template("register.html")


# --------------------
# LOGIN
# --------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return "Missing fields", 400

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            flash("Invalid username or password")
            return redirect("/login")

        session["user_id"] = rows[0]["id"]
        return redirect("/")

    return render_template("login.html")


# --------------------
# LOGOUT
# --------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# --------------------
# ADD FLASHCARD
# --------------------
@app.route("/add", methods=["GET", "POST"])
def add_flashcard():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        question = request.form.get("question")
        answer = request.form.get("answer")
        if not question or not answer:
            flash("Missing question or answer")
            return redirect("/add")

        db.execute(
            "INSERT INTO flashcards (user_id, question, answer) VALUES (?, ?, ?)",
            session["user_id"], question, answer
        )
        return redirect("/")

    return render_template("add.html")


@app.route("/study")
def study():
    if "user_id" not in session:
        return redirect("/login")

    rows = db.execute("SELECT * FROM flashcards WHERE user_id = ?", session["user_id"])
    return render_template("study.html", cards=rows)


# --------------------
# EDIT FLASHCARD
# --------------------
@app.route("/edit/<int:card_id>", methods=["GET", "POST"])
def edit_flashcard(card_id):
    if "user_id" not in session:
        return redirect("/login")

    # Fetch the card, ensure it belongs to the user
    card = db.execute("SELECT * FROM flashcards WHERE id = ? AND user_id = ?", card_id, session["user_id"])
    if not card:
        flash("Flashcard not found.")
        return redirect("/")
    card = card[0]

    if request.method == "POST":
        question = request.form.get("question")
        answer = request.form.get("answer")
        if not question or not answer:
            flash("Missing question or answer.")
            return redirect(f"/edit/{card_id}")
        db.execute("UPDATE flashcards SET question = ?, answer = ? WHERE id = ? AND user_id = ?", question, answer, card_id, session["user_id"])
        flash("Flashcard updated!")
        return redirect("/")

    return render_template("edit.html", card=card)


# --------------------
# DELETE FLASHCARD
# --------------------
@app.route("/delete/<int:card_id>", methods=["POST"])
def delete_flashcard(card_id):
    if "user_id" not in session:
        return redirect("/login")
    db.execute("DELETE FROM flashcards WHERE id = ? AND user_id = ?", card_id, session["user_id"])
    flash("Flashcard deleted.")
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
