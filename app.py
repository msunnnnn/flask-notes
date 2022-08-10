from flask import Flask, flash, redirect, render_template, session, abort, g

from models import db, connect_db, User, Note
from forms import NoteForm, RegisterForm, LoginForm, CSRFProtectForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "oh-so-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///notes"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

connect_db(app)
db.create_all()

# def check_login_status(func):
#     def inner():
#         if "username" not in session:
#             flash("You must be logged in to view!")
#             return redirect("/login")
#         # elif session["username"] != username:
#         #     flash("You are not authorized!")
#         #     return redirect(f"/users/{username}")
#     return inner

@app.before_request
def add_csrf_form_to_all_pages():
    """Before every route, add CSRF-only form to global object."""
    g.csrf_form = CSRFProtectForm()


@app.get('/')
def redirect_home_page():
    """Redirects to login page."""
    return redirect('/login')

######## User ##########

@app.route('/register', methods = ["GET", "POST"])
def show_register_form():
    """Shows registration form for user, accepts user data and adds
    to database."""

    if "username" in session:
        return redirect(f'/users/{session["username"]}')

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        if User.query.get(username):
            flash("invalid username")
            return render_template("register.html", form = form)

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

    if "username" not in session:
        flash("You must be logged in to view!")
        return redirect("/login")

    if session["username"] != username:
        flash("You are not authorized!")
        return abort(401)
        # return redirect(f"/users/{username}")

    form = CSRFProtectForm()
    user = User.query.get_or_404(username)
    return render_template("user.html", user = user, form = form)

@app.post("/logout")
def logout():
    """Logs user out and redirects to homepage."""

    # form = CSRFProtectForm()

    if g.csrf_form.validate_on_submit():
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
        # form = CSRFProtectForm()

        if g.csrf_form.validate_on_submit():
        # Remove "username" if present, but no errors if it wasn't
            Note.query.filter_by(owner=username).delete()
            user = User.query.get_or_404(username)
            user.query.delete()

            db.session.commit()

            session.pop("username")
        return redirect('/login')

######## NOTES ##########

@app.route("/users/<username>/notes/add", methods=["GET","POST"])
def show_add_note_form(username):
    """Shows add note form for user."""
    # TODO: break into 2 ifs
    if "username" not in session or session["username"] != username:
        flash("You must be logged in to view!")
        return redirect("/login")

    else:
        form = NoteForm()
        user = User.query.get_or_404(username)


        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data

            new_note = Note(title=title, content=content, owner=username)

            db.session.add(new_note)
            db.session.commit()

            return redirect(f'/users/{username}')

        else:
            return render_template("addnote.html", form=form, user=user)

@app.get('/notes/<int:note_id>')
def show_note(note_id):
    """Show note page"""

    note = Note.query.get_or_404(note_id)
    if "username" not in session or session["username"] != note.owner:
        flash("You must be logged in to view!")
        return redirect("/login")

    return render_template("note.html", note = note)

@app.route('/notes/<note_id>/update', methods = ["GET", "POST"])
def edit_note(note_id):
    """Shows edit note form for user"""

    note = Note.query.get_or_404(note_id)
    form = NoteForm(obj = note)

    if "username" not in session or session["username"] != note.owner:
        flash("You must be logged in to view!")
        return redirect("/login")

    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data

        db.session.commit()
        flash(f'{note.title} updated')
        return redirect (f'/users/{note.owner}')

    else:
        return render_template("editnote.html", form = form, note = note)

@app.post('/notes/<note_id>/delete')
def delete_note(note_id):
    """Deletes note of logged in user."""

    note = Note.query.get_or_404(note_id)
    user = User.query.get_or_404(note.owner)
# look at decorators to not type so much
    if "username" not in session or session["username"] != user.username:
        flash("You must be logged in to view!")
        return redirect("/login")

    else:
        # form = CSRFProtectForm()

        if g.csrf_form.validate_on_submit():
            Note.query.filter_by(id = note_id).delete()
            db.session.commit()

        flash('Note deleted')
        return redirect(f'/users/{user.username}')
