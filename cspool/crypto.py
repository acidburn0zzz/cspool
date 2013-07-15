import os
from nacl import public


class Error(Exception):
    pass


class TestBox(object):
    """Fake crypto for testing."""

    def encrypt(self, data):
        pk = public.PublicKey(public_key)
        return '{crypt}' + data

    def decrypt(self, data):
        if not data.startswith('{crypt}'):
            raise Error('decryption error')
        return data[7:]


class Box(object):
    """Crypto box for safe communication between two keypairs."""

    def __init__(self, username, src_key, dst_key):
        self._prefix = username
        self._src = src_key
        self._dst = dst_key
        self._box = public.Box(
            public.PrivateKey(src_key),
            public.PublicKey(dst_key))

    def encrypt(self, data):
        r = os.urandom(max(0, self._box.NONCE_SIZE - len(self._prefix)))
        nonce = (self._prefix + r)[-self._box.NONCE_SIZE:]
        print 'nonce:', nonce, self._box.NONCE_SIZE, len(r)
        return self._box.encrypt(data, nonce)

    def decrypt(self, ciphertext):
        return self._box.decrypt(ciphertext)


if __name__ == '__main__':
    # Generate a secret/public keypair.
    import sys
    if len(sys.argv) != 3:
        print >>sys.stderr, "Usage: crypto.py <secret-key-file> <public-key-file>"
        sys.exit(1)
    secret_key_path, public_key_path = sys.argv[1:]
    key = public.PrivateKey.generate()
    with open(secret_key_path, 'w') as fd:
        fd.write(bytes(key))
    with open(public_key_path, 'w') as fd:
        fd.write(bytes(key.public_key))

