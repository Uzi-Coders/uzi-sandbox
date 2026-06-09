import re


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
