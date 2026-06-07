from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_user, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from database.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired("Username is required.")])
    password = PasswordField('Password', validators=[DataRequired("Password is required.")])
    submit = SubmitField('Login')


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        form.username.errors.append('Invalid username or password.')
    return render_template('login.html', form=form)


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
