import base64


def encode(text):
    max_len = 9
    if not isinstance(text, str):
        text = str(text)
    while len(text) < max_len:
        text = '0' + text
    print(text)
    return base64.b64encode(text)


def decode(text):
    return int(base64.b64decode(text))
