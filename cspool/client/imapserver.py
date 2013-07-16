import email
import getpass
import logging
import time
import optparse

from twisted.mail import imap4
from twisted.internet import reactor, defer, protocol
from twisted.cred import portal
from zope.interface import implements

from cspool.crypto import Box
from cspool.client.db import Database
from cspool.client.imap_interface import SingleUserCredentialsChecker, UserAccount
from cspool.client.server_stub import ServerStub
from cspool.client.sync import Syncer


class MailUserRealm(object):
    """Connect the IMAP server with our UserAccount objects."""
    
    implements(portal.IRealm)

    avatarInterfaces = {
        imap4.IAccount: UserAccount,
        }

    def __init__(self, db, box, spool_stub):
        self._db = db
        self._box = box
        self._spool = spool_stub

    def requestAvatar(self, avatarId, mind, *interfaces):
        for requestedInterface in interfaces:
            if self.avatarInterfaces.has_key(requestedInterface):
                # return an instance of the correct class
                avatarClass = self.avatarInterfaces[requestedInterface]
                avatar = avatarClass(self._db, self._box, self._spool)
                # null logout function: take no arguments and do nothing
                logout = lambda: None
                return defer.succeed((requestedInterface, avatar, logout))

        raise KeyError('None of the requested interfaces is supported')


class IMAPServerProtocol(imap4.IMAP4Server):
    """Subclass of imap4.IMAP4Server that adds debugging."""

    debug = True

    def lineReceived(self, line):
        if self.debug:
            print "CLIENT:", line
        imap4.IMAP4Server.lineReceived(self, line)

    def sendLine(self, line):
        imap4.IMAP4Server.sendLine(self, line)
        if self.debug:
            print "SERVER:", line


class IMAPFactory(protocol.Factory):

    protocol = IMAPServerProtocol
    portal = None # placeholder

    def buildProtocol(self, address):
        p = self.protocol()
        p.portal = self.portal
        p.factory = self
        return p


def box_from_opts(opts):
    with open(opts.user_key) as fd:
        secret_key = fd.read()
    with open(opts.spool_key) as fd:
        public_key = fd.read()
    return Box(opts.user, secret_key, public_key)


def main():
    parser = optparse.OptionParser()
    parser.add_option('--port', default=1143, type='int',
                      help='TCP port where the IMAP server should listen on')
    parser.add_option('--user', default=getpass.getuser(),
                      help='Username for authentication')
    parser.add_option('--password', help='Password for the local IMAP account')
    parser.add_option('--db', default='test.db',
                      help='Path to the SQLite database file')
    parser.add_option('--spool-server',
                      dest='spool_server_url',
                      default='http://localhost:3999',
                      help='URL of the spool server')
    parser.add_option('--user-key', dest='user_key',
                      help='Secret key to use for decryption')
    parser.add_option('--spool-key', dest='spool_key',
                      help='Public key of the spool, to use for verification')
    opts, args = parser.parse_args()

    if not opts.user_key or not opts.spool_key:
        parser.error('Must specify both --user-key and --spool-key')

    logging.basicConfig()

    db = Database(opts.db)
    server = ServerStub(opts.spool_server_url, opts.user)
    box = box_from_opts(opts)
    sync = Syncer(db, server, box)
    sync.setDaemon(True)
    sync.start()

    p = portal.Portal(MailUserRealm(db, box, server))
    p.registerChecker(SingleUserCredentialsChecker(opts.user, opts.password))

    factory = IMAPFactory()
    factory.portal = p

    reactor.listenTCP(opts.port, factory)
    reactor.run()


if __name__ == "__main__":
    main()
