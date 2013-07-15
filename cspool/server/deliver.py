from cspool.crypto import encrypt
from cspool.proto import PutCommand
from cspool.server.spool import Spool
from cspool.server.userdb import get_key_for_user
import optparse
import sys
import time


def deliver(msg, user):
    Spool(user).append(
        encrypt(get_key_for_user(user),
                PutCommand((msg, time.time())).serialize()))


def main():
    parser = optparse.OptionParser()
    parser.add_option('--user', help='Destination user')
    opts, args = parser.parse_args()
    if not opts.user:
        parser.error('Must specify --user')

    msg = sys.stdin.read()
    deliver(msg, opts.user)


if __name__ == '__main__':
    main()
