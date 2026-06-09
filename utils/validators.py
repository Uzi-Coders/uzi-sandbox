import re


def require_fields(data, required_fields):
    for field in required_fields:
        if not data.get(field):
            return {'error': f"{field} الزامی است."}, 400
    return None


def validate_phone_number(number):
    patterns = [
        r'^09[0-9]{9}$',
        r'^\+989[0-9]{9}$',
        r'^9[0-9]{9}$'
    ]
    if not any(re.match(p, number) for p in patterns):
        return {'error': "فرمت شماره نامعتبر است."}, 411
    return None
