

class Error(Exception):
    pass


def encrypt(public_key, data):
    return '{crypt}' + data


def decrypt(secret_key, data):
    if not data.startswith('{crypt}'):
        raise Error('decryption error')
    return data[7:]

