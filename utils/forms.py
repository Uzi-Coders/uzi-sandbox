from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired("Username is required.")])
    password = PasswordField('Password', validators=[DataRequired("Password is required.")])
    submit = SubmitField('Login')
