from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, ValidationError
from sqlalchemy import select
from models import User
from flask import g

def unique_username():
    """Ensure username is available"""
    message = "That username is already taken. Please enter a unique username."

    def _unique(form, field):
        username = field.data
        database_entry = User.query.filter_by(username = username).all()
        if database_entry:
            if username != g.user.username:
                raise ValidationError(message)
    return _unique

def unique_email():
    """Checks the database for a unique email."""
    message = "That email is already associated with another user. Please enter a unique email."

    def _unique(form,field):
        email = field.data
        database_entry = User.query.filter_by(email=email).all()
        if database_entry:
            if email != g.user.email:
                raise ValidationError(message)
    return _unique

class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')
 

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class UpdateUser(FlaskForm):
    """Option to update the user information."""
    username = StringField('Username', validators=[DataRequired(), unique_username()])
    email = StringField('E-mail', validators=[Email(), unique_email()])
    image_url = StringField('(Optional) Image URL')
    header_image_url = StringField('(Optional) Header Image URL')
    location = StringField('(Optional) Location')
    bio = StringField('(Optional) Biography')
    password = PasswordField('Password')