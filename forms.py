from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
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
    username = StringField('Username',
                            validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Password',
                            validators=[InputRequired(), Length(min=8, max=20)])