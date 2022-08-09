from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Optional, Email, Length

class RegisterForm(FlaskForm):
    """Form for registering a new user."""
    username = StringField('Username',
                            validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Password',
                            validators=[InputRequired(), Length(min=8, max=20)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    first_name = StringField('First Name',
                             validators=[InputRequired(), Length(min=2, max=30)])
    last_name = StringField('Last Name',
                            validators=[InputRequired(), Length(min=2, max=30)])

class LoginForm(FlaskForm):
    """Form for login"""
    username = StringField('Username',
                            validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Password',
                            validators=[InputRequired(), Length(min=8, max=20)])

class CSRFProtectForm(FlaskForm):
    """Form just for CSRF Protection"""

class AddNoteForm(FlaskForm):
    """Form for adding a new note."""
    title = StringField('Title',
                        validators=[InputRequired(), Length(min=2, max=100)])
    content = TextAreaField('Content',
                        validators=[InputRequired()])
