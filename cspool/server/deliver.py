"""Deliver a message to the local spool, encrypting it."""

from cspool.proto import PutCommand
from cspool.server.spool import Spool
from cspool.server.userdb import TestUserDb
import optparse
import sys
import time


def deliver(msg, user, user_db):
    Spool(user).append(
        user_db.get_cryptobox(user).encrypt(
            PutCommand((msg, time.time())).serialize()))


def main():
    parser = optparse.OptionParser()
    parser.add_option('--user', help='Destination user')
    parser.add_option('--user-key', dest='user_key',
                      help='User public key to use for encryption')
    parser.add_option('--server-key', dest='server_key',
                      help='Server secret key to user for signing')
    opts, args = parser.parse_args()
    if not opts.user:
        parser.error('Must specify --user')
    if not opts.user_key:
        parser.error('Must specify --user-key')
    if not opts.server_key:
        parser.error('Must specify --server-key')

    msg = sys.stdin.read()
    user_db = TestUserDb(opts.server_key, opts.user_key)
    deliver(msg, opts.user, user_db)


if __name__ == '__main__':
    main()
