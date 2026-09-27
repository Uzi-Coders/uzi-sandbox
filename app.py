import os
import pathlib
from flask import Flask, render_template
from dotenv import load_dotenv
from flask_login import LoginManager, login_required
from blueprints import auth, sms, gateway

from database.db import db
from database.models import User

BASE_DIR = pathlib.Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

app = Flask(__name__, static_url_path='/sandbox/static')

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
if not app.config['SECRET_KEY']:
    raise RuntimeError(
        "SECRET_KEY is not set. Copy .env.example to .env and set a long random value, "
        "or export SECRET_KEY in the environment."
    )
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + str(BASE_DIR / 'database' / 'db.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/sandbox/')
@login_required
def index():
    return render_template('index.html')


app.register_blueprint(auth.auth_bp)
app.register_blueprint(sms.sms_bp)
app.register_blueprint(gateway.gateway_bp)
