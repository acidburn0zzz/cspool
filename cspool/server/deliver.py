"""Deliver a message to the local spool, encrypting it."""

from cspool.proto import PutCommand
from cspool.server.spool import Spool
from cspool.server.userdb import TestUserDb
import optparse
import sys
import time


def encrypt_msg(msg, user, user_db):
    return user_db.get_cryptobox(user).encrypt(
            PutCommand((msg, time.time())).serialize())


def deliver(msg, user, user_db):
    Spool(user).append(encrypt_msg(msg, user, user_db))


def main():
    parser = optparse.OptionParser()
    parser.add_option('--user', help='Destination user')
    parser.add_option('--user-key', dest='user_key',
                      help='User public key to use for encryption')
    parser.add_option('--spool-key', dest='spool_key',
                      help='Spool secret key to use for signing')
    opts, args = parser.parse_args()
    if not opts.user:
        parser.error('Must specify --user')
    if not opts.user_key:
        parser.error('Must specify --user-key')
    if not opts.spool_key:
        parser.error('Must specify --spool-key')

    msg = sys.stdin.read()
    with open(opts.user_key) as fd:
        public_key = fd.read()
    with open(opts.spool_key) as fd:
        private_key = fd.read()

    user_db = TestUserDb(private_key, public_key)
    deliver(msg, opts.user, user_db)


if __name__ == '__main__':
    main()
