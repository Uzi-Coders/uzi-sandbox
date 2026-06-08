import uuid
from random import randint
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from .db import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    api_key = db.Column(db.String(64), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    sms_sender = db.Column(db.Integer(), default=randint(10000, 99999))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User %r>' % self.username


class SmsLog(db.Model):
    __tablename__ = 'sms_logs'

    id = db.Column(db.Integer, primary_key=True)
    receptor = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text(), nullable=False)
    date = db.Column(db.DateTime(), nullable=False, default=datetime.now)
    statustext = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Integer(), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User')

    def __repr__(self):
        return '<SmsLog %r>' % self.message
