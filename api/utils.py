import base64
from datetime import datetime

DATETIME_FROMAT = '%S%y%H%m%M%d%f'


def encode(text):
    max_len = 9
    if not isinstance(text, str):
        text = str(text)
    while len(text) < max_len:
        text = '0' + text
    return base64.b64encode(text)


def decode(text):
    return int(base64.b64decode(text))


def get_now_string():
    return datetime.now().strftime(DATETIME_FROMAT)


def string_to_date(date):
    return datetime.strptime(date, DATETIME_FROMAT)
