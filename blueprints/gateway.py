from flask import Blueprint, request, render_template, jsonify
from utils.decorators import require_api_key
from utils.validators import validate_phone_number, validate_email, require_fields
from utils.helpers import normalize_phone_number
from urllib.parse import urlparse
from database.models import PaymentTransaction
from database.db import db

gateway_bp = Blueprint('gateway', __name__, url_prefix='/gateway')


def validate_payment_data(data):
    error = require_fields(data, ['order_id', 'amount', 'callback'])
    if error:
        return error

    if not isinstance(data['order_id'], str):
        return {'error': "شناسه سفارش (order_id) باید از نوع رشته (string) باشد."}, 400
    if not isinstance(data['amount'], int):
        return {'error': "مبلغ (amount) باید از نوع عدد باشد."}, 400
    if not isinstance(data['callback'], str):
        return {'error': "آدرس بازگشت (callback) باید از نوع رشته (string) باشد."}, 400

    if data['amount'] < 1000:
        return {'error': "مبلغ باید حداقل ۱,۰۰۰ ریال باشد."}, 400
    if data['amount'] > 500_000_000:
        return {'error': "مبلغ نمی تواند بیشتر از ۵۰۰,۰۰۰,۰۰۰ ریال باشد."}, 400

    parsed = urlparse(data['callback'])
    if parsed.scheme not in ('http', 'https'):
        return {'error': "آدرس بازگشت باید HTTP یا HTTPS باشد."}, 400
    if not parsed.netloc:
        return {'error': "آدرس بازگشت معتبر نیست."}, 400

    if 'name' in data and not isinstance(data['name'], str):
        return {'error': "نام (name) باید از نوع رشته (string) باشد."}, 400
    if 'phone' in data:
        if not isinstance(data['phone'], str):
            return {'error': "شماره (phone) باید از نوع رشته (string) باشد."}, 400
        error = validate_phone_number(data['phone'])
        if error:
            return error

    if 'mail' in data:
        if not isinstance(data['mail'], str):
            return {'error': "ایمیل (mail) باید از نوع رشته (string) باشد."}, 400
        error = validate_email(data['mail'])
        if error:
            return error

    if 'desc' in data and not isinstance(data['desc'], str):
        return {'error': "توضیحات (desc) باید از نوع رشته (string) باشد."}, 400

    return None


@gateway_bp.route('/payment', methods=['POST'])
@require_api_key
def payment():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': "بدنه درخواست باید از نوع JSON باشد."}), 400

    error = validate_payment_data(data)
    if error:
        return jsonify(error[0]), error[1]

    transaction = PaymentTransaction(
        order_id=data['order_id'],
        amount=data['amount'],
        callback=data['callback'],
        name=data['name'] if 'name' in data else None,
        phone=normalize_phone_number(data['phone']) if 'phone' in data else None,
        mail=data['mail'] if 'mail' in data else None,
        desc=data['desc'] if 'desc' in data else None,
        user_id=request.current_user.id
    )
    db.session.add(transaction)
    db.session.commit()

    return jsonify(
        {'id': transaction.transaction_id, 'link': f"{request.host_url.rstrip('/')}/fake-pay/{transaction.link}"}), 201
