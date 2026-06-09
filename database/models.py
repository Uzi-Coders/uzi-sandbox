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
    user = db.relationship('User', backref=db.backref('sms_logs', lazy='dynamic'))

    def __repr__(self):
        return '<SmsLog %r>' % self.message


class PaymentTransaction(db.Model):
    __tablename__ = 'payment_transactions'

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(32), nullable=False, unique=True, index=True)
    order_id = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(13), nullable=True)
    mail = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    callback = db.Column(db.String(2048), nullable=False)
    status = db.Column(db.Integer, nullable=False, default=1)
    track_id = db.Column(db.String(50), nullable=True)
    card_no = db.Column(db.String(20), nullable=True)
    hashed_card_no = db.Column(db.String(255), nullable=True)
    payment_date = db.Column(db.DateTime, nullable=True)
    verify_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('payment_transactions', lazy='dynamic'))

    def __repr__(self):
        return '<PaymentTransaction %r>' % self.transaction_id
