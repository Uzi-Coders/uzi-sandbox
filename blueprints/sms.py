import re
from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from utils.decorators import require_api_key
from database.models import SmsLog
from database.db import db

sms_bp = Blueprint('sms', __name__, url_prefix='/sms')


@sms_bp.route('/panel')
@login_required
def panel():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    paginated_logs = SmsLog.query.filter_by(user_id=current_user.id).order_by(SmsLog.date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('sms_panel.html', logs=paginated_logs)


def validate_sms_data(data):
    if not data.get('receptor'):
        return {'error': "شماره گیرنده (receptor) الزامی است."}, 400
    if not data.get('message'):
        return {'error': "متن پیام (message) الزامی است."}, 400

    if not isinstance(data['receptor'], str):
        return {'error': "شماره گیرنده باید از نوع رشته (string) باشد."}, 400
    if not isinstance(data['message'], str):
        return {'error': "متن پیام باید از نوع رشته (string) باشد."}, 400

    if len(data['message']) > 900:
        return {'error': "طول متن پیام نباید بیشتر از 900 کاراکتر باشد."}, 413

    receptor = data['receptor'].strip()
    patterns = [
        r'^09[0-9]{9}$',
        r'^\+989[0-9]{9}$',
        r'^9[0-9]{9}$'
    ]
    if not any(re.match(p, receptor) for p in patterns):
        return {'error': "فرمت شماره گیرنده نامعتبر است."}, 411
    return None


def normalize_phone_number(number):
    number = number.strip()

    if re.match(r'^09[0-9]{9}$', number):
        return number

    elif re.match(r'^\+989[0-9]{9}$', number):
        return '0' + number[3:]

    elif re.match(r'^9[0-9]{9}$', number):
        return '0' + number

    else:
        return number


@sms_bp.route('/send', methods=['POST'])
@require_api_key
def send():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': "بدنه درخواست باید از نوع JSON باشد."}), 400

    error = validate_sms_data(data)
    if error:
        return jsonify(error[0]), error[1]

    log = SmsLog(
        message=data['message'],
        receptor=normalize_phone_number(data['receptor']),
        status=10,
        statustext="رسیده به گیرنده",
        user_id=request.current_user.id
    )

    db.session.add(log)
    db.session.commit()

    return jsonify({
        'return': {
            'status': 200,
            'message': "تایید شد"},
        'entries': {
            'messageid': log.id,
            'message': log.message,
            'status': log.status,
            'statustext': log.statustext,
            'sender': log.user.sms_sender,
            'receptor': log.receptor,
            'date': int(log.date.timestamp()),
        }
    })
