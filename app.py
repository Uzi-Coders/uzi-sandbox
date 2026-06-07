import os
import pathlib
from flask import Flask
from dotenv import load_dotenv
from flask_login import LoginManager

from database.db import db
from database.models import User

BASE_DIR = pathlib.Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + str(BASE_DIR / 'database' / 'db.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

with app.app_context():
    db.create_all()
