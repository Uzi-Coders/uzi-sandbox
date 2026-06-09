import uuid
import random
from datetime import datetime
from flask import Blueprint, request, render_template, jsonify, abort, redirect
from flask_login import login_required, current_user
from utils.decorators import require_api_key
from utils.validators import validate_phone_number, validate_email, require_fields
from utils.helpers import normalize_phone_number, generate_random_card_number, hash_card_number
from urllib.parse import urlparse
from database.models import PaymentTransaction
from database.db import db

gateway_bp = Blueprint('gateway', __name__, url_prefix='/gateway')


@gateway_bp.route('/panel', methods=['GET'])
@login_required
def panel():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    paginated = (PaymentTransaction.query.filter_by(user_id=current_user.id)
                 .order_by(PaymentTransaction.created_at.desc())
                 .paginate(page=page, per_page=per_page, error_out=False))

    return render_template('gateway_panel.html', transactions=paginated)


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
        transaction_id=str(uuid.uuid4().hex),
        name=data['name'] if 'name' in data else None,
        phone=normalize_phone_number(data['phone']) if 'phone' in data else None,
        mail=data['mail'] if 'mail' in data else None,
        description=data['desc'] if 'desc' in data else None,
        user_id=request.current_user.id
    )
    db.session.add(transaction)
    db.session.commit()

    return jsonify(
        {'id': transaction.transaction_id,
         'link': f"{request.host_url.rstrip('/')}/gateway/fake-pay/{transaction.transaction_id}"}), 201


@gateway_bp.route('/fake-pay/<string:transaction_id>', methods=['GET', 'POST'])
def fake_pay(transaction_id):
    transaction = PaymentTransaction.query.filter_by(transaction_id=transaction_id).first_or_404()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'confirm':
            masked_card, full_card = generate_random_card_number()
            card_hash = hash_card_number(full_card)

            transaction.status = 10
            transaction.track_id = str(random.randint(10000, 99999))
            transaction.card_no = masked_card
            transaction.hashed_card_no = card_hash
            transaction.payment_date = datetime.now()
            db.session.commit()

            return redirect(
                f"{transaction.callback}?status={transaction.status}&track_id={transaction.track_id}&id={transaction.transaction_id}&order_id={transaction.order_id}&amount={transaction.amount}&card_no={masked_card}")

        transaction.status = 2
        db.session.commit()
        return redirect(
            f"{transaction.callback}?status={transaction.status}&id={transaction.transaction_id}&order_id={transaction.order_id}")

    if transaction.status == 1:
        return render_template('fake_pay.html', transaction=transaction)
    abort(404)


@gateway_bp.route('/payment/verify', methods=['POST'])
@require_api_key
def payment_verify():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': "بدنه درخواست باید JSON باشد."}), 400

    transaction_id = data.get('id')
    order_id = data.get('order_id')
    if not transaction_id or not order_id:
        return jsonify(
            {'error_code': 31, 'error_message': "کد تراکنش (id) یا شماره سفارش (order_id) نباید خالی باشد."}), 406

    if not isinstance(transaction_id, str) or not isinstance(order_id, str):
        return jsonify({'error_code': 31, 'error_message': "پارامترها باید از نوع رشته باشند."}), 406

    transaction = PaymentTransaction.query.filter_by(transaction_id=transaction_id, order_id=order_id).first()
    if not transaction:
        return jsonify({'error_code': 52, 'error_message': "استعلام نتیجه ای نداشت."}), 400

    if transaction.status == 10:
        transaction.status = 100
        transaction.verify_date = datetime.now()
        db.session.commit()

        return jsonify({
            "status": "100",
            "track_id": transaction.track_id,
            "id": transaction.transaction_id,
            "order_id": transaction.order_id,
            "amount": str(transaction.amount),
            "date": str(int(transaction.created_at.timestamp())),
            "payment": {
                "track_id": transaction.track_id,
                "amount": str(transaction.amount),
                "card_no": transaction.card_no,
                "hashed_card_no": transaction.hashed_card_no,
                "date": str(int(transaction.payment_date.timestamp()))
            },
            "verify": {
                "date": str(int(transaction.verify_date.timestamp()))
            }
        }), 200

    return jsonify({'error_code': 53, 'error_message': 'تایید پرداخت امکان پذیر نیست.'}), 405
