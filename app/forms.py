from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, URLField
from wtforms.validators import DataRequired, Length, EqualTo, URL, Optional, NumberRange


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message="Username is required."),
        Length(min=4, max=25, message="Username must be between 4 and 25 characters.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required."),
        Length(min=8, message="Password must be at least 8 characters.")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Please confirm your password."),
        EqualTo('password', message="Passwords must match.")
    ])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message="Username is required.")])
    password = PasswordField('Password', validators=[DataRequired(message="Password is required.")])
    submit = SubmitField('Log In')


class PasswordForm(FlaskForm):
    title = StringField('Title', validators=[Optional()])
    username = StringField('Username', validators=[Optional()])
    password = PasswordField('Password', validators=[Optional()])
    url = URLField('URL', validators=[Optional(), URL(message="Invalid URL.")])
    submit = SubmitField('Add Password')


class GeneratePasswordForm(FlaskForm):
    length = IntegerField('Length', validators=[
        DataRequired(message="Password length is required."),
        NumberRange(min=4, max=64, message="Length must be between 4 and 64.")
    ])
    submit = SubmitField('Generate')
class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message="Current password is required.")
    ])
    new_password = PasswordField('New Password', validators=[
        DataRequired(message="New password is required."),
        Length(min=8, message="New password must be at least 8 characters.")
    ])
    confirm_new_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message="Please confirm your new password."),
        EqualTo('new_password', message="Passwords must match.")
    ])
    submit = SubmitField('Change Password')


class DeleteAccountForm(FlaskForm):
    confirm_username = StringField('Confirm Username', validators=[
        DataRequired(message="Please confirm your username.")
    ])
    submit = SubmitField('Delete Account')

