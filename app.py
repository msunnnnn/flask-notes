from flask import Flask, flash, redirect, render_template, session

from models import db, connect_db, User, Note
from forms import AddNoteForm, RegisterForm, LoginForm, CSRFProtectForm

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
        session["username"] = username
        return redirect(f'/users/{username}')

    return render_template('register.html', form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Produce login form or handle login."""

    if "username" in session:
        return redirect(f'/users/{session["username"]}')

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # authenticate will return a user or False
        user = User.authenticate(username, password)

        if user:
            session["username"] = user.username  # keep logged in
            return redirect(f'/users/{username}')

        else:
            form.username.errors = ["Bad name/password"]

    return render_template("login.html", form=form)


@app.get("/users/<username>")
def display_user_profile(username):
    """Display user profile of logged in user."""

    if "username" not in session or session["username"] != username:
        flash("You must be logged in to view!")
        return redirect("/login")

    else:
        form = CSRFProtectForm()
        user = User.query.get(username)
        return render_template("user.html", user = user, form = form)

@app.post("/logout")
def logout():
    """Logs user out and redirects to homepage."""

    form = CSRFProtectForm()

    if form.validate_on_submit():
        # Remove "username" if present, but no errors if it wasn't
        session.pop("username", None)

    return redirect("/")

@app.post("/users/<username>/delete")
def delete_user_profile(username):
    """Deletes user profile of logged in user."""

    if "username" not in session or session["username"] != username:
        flash("You must be logged in to view!")
        return redirect("/login")

    else:
        form = CSRFProtectForm()

        if form.validate_on_submit():
        # Remove "username" if present, but no errors if it wasn't
            Note.query.filter_by(owner=username).delete()
            user = User.query.get(username)
            user.query.delete()

            db.session.commit()

            session.pop("username")
        return redirect('/login')

@app.route("/users/<username>/notes/add", methods=["GET","POST"])
def show_add_note_form(username):
    """Shows add note form for user."""

    if "username" not in session or session["username"] != username:
        flash("You must be logged in to view!")
        return redirect("/login")

    else:
        form = AddNoteForm()
        user = User.query.get(username)

        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data

            new_note = Note(title=title, content=content, owner=username)

            db.session.add(new_note)
            db.session.commit()

            return redirect('/users/<username>')

        else:
            return render_template("addnote.html", form=form, user=user)