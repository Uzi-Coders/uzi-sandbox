from functools import wraps
from flask import request, jsonify
from database.models import User


def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': "هدر X-API-Key ارسال نشده است."}), 401

        user = User.query.filter_by(api_key=api_key).first()
        if not user:
            return jsonify({'error': "کلید API نامعتبر است."}), 401

        request.current_user = user
        return f(*args, **kwargs)

    return decorated
