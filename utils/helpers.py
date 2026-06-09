import re
import random
import hashlib


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


def generate_random_card_number():
    full_number = ''.join(str(random.randint(0, 9)) for _ in range(16))
    masked = full_number[:6] + '******' + full_number[-4:]
    return masked, full_number


def hash_card_number(card_number):
    return hashlib.sha256(card_number.encode()).hexdigest().upper()
