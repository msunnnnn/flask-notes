from flask import Flask, flash, redirect, render_template, session

from models import db, connect_db, User
from forms import RegisterForm, LoginForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "oh-so-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///notes"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

connect_db(app)
db.create_all()

@app.get('/')
def redirect_home_page():
    """Redirects to register page."""
    return redirect('/register')

@app.route('/register', methods = ["GET", "POST"])
def show_register_form():
    """Shows registration form for user, accepts user data and adds
    to database."""

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User.register(username=username,
                  password=password,
                  email=email,
                  first_name=first_name,
                  last_name=last_name)

        db.session.add(user)
        db.session.commit()

        flash(f"Created account for {username}")
        return redirect("/login")

    return render_template('register.html', form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Produce login form or handle login."""

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # authenticate will return a user or False
        user = User.authenticate(username, password)

        if user:
            session["username"] = user.username  # keep logged in
            return redirect("/secret")

        else:
            form.username.errors = ["Bad name/password"]

    return render_template("login.html", form=form)


@app.get("/secret")
def secret():
    """Example hidden page for logged-in users only."""

    if "username" not in session:
        flash("You must be logged in to view!")
        return redirect("/login")

    else:
        return render_template("secret.html")

