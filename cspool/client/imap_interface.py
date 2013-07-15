from twisted.mail import imap4
from zope.interface import implements
from twisted.internet import defer, protocol
from twisted.cred import checkers, credentials
import StringIO
import time
import rfc822


class Error(Exception):
    pass


class CredentialsChecker(object):
    implements(checkers.ICredentialsChecker)
    credentialInterfaces = (credentials.IUsernamePassword,)

    def __init__(self):
        print 'Initialized credentials checker.'
        pass

    def requestAvatarId(self, credentials):
        print 'Got login request for username=%s' % credentials.username
        return defer.succeed(credentials.username)


class UserAccount(object):
    implements(imap4.IAccount)

    def __init__(self, db):
        self._db = db

    def listMailboxes(self, ref, wildcard):
        mail_boxes = {'INBOX': Mailbox(self._db)}
        return defer.succeed(mail_boxes.items())

    def select(self, path, rw=True):
        if path.upper() != 'INBOX':
            raise Error('unknown folder "%s"' % path)
        return Mailbox(self._db)

    def close(self):
        return True

    def create(self, path):
        return False

    def delete(self, path):
        return False

    def rename(self, oldname, newname):
        return False

    def isSubscribed(self, path):
        return True

    def subscribe(self, path):
        return True

    def unsubscribe(self, path):
        return True


class Mailbox(object):
    implements(imap4.IMailbox)

    def __init__(self, db):
        self._db = db
        self._uid_map = {}
        self.listeners = []

    def getHierarchicalDelimiter(self):
        return '.'

    def getFlags(self):
        return ['\\Seen', '\\Unseen', '\\Flagged', '\\Answered', '\\HasNoChildren']

    def getMessageCount(self):
        return self._db.count_messages()

    def getRecentCount(self):
        return self._db.count_messages(unread=True)

    getUnseenCount = getRecentCount

    def isWriteable(self):
        return True

    def getUIDValidity(self):
        return 0

    def getUID(self, messageNum):
        raise imap4.MailboxException('Not implemented')

    def getUIDNext(self):
        return 1

    def fetch(self, messages, uid):
        print 'FETCH: MESSAGES:', messages, 'UID:', uid

        counter = 0
        if uid:
            try:
                uid = len(messages)
            except TypeError:
                print 'uh, funny type:', messages
                uid = 0

        if uid:
            ids = []
            first = 0
            for id in messages:
                if first == 0:
                    first = id
                ids.append(self._uid_map[id])
            counter = first - 1
            msgs = self._db.fetch_headers(ids)
        else:
            msgs = self._db.fetch_headers()

        for info, msg in msgs:
            counter += 1
            info['counter'] = counter
            self._uid_map[counter] = info['id']
            yield counter, Message(info, msg, self._db)

    def addListener(self, listener):
        self.listeners.append(listener)
        return True

    def removeListener(self, listener):
        self.listeners.remove(listener)
        return True

    def requestStatus(self, names):
        r = {}
        for n in names:
            r[n] = getattr(self, _statusRequestDict[n.upper()])()
        return r

    def addMessage(self, msg, flags=None, date=None):
        raise imap4.MailboxException('Not implemented')

    def store(self, messageSet, flags, mode, uid):
        for id in messageSet:
            msgid = self._uid_map[id]
            if '\\Seen' in flags:
                seen = (mode == -1) and 0 or 1
                self._db.set_flag_on_message(msgid, 'seen', seen)
            if '\\Deleted' in flags:
                deleted = (mode == -1) and 0 or 1
                self._db.set_flag_on_message(msgid, 'deleted', deleted)

    def expunge(self):
        self._db.expunge()

    def destroy(self):
        raise imap4.MailboxException('Not implemented')


class Message(object):
    implements(imap4.IMessage)

    def __init__(self, info, msg, db):
        self._db = db
        self._msg = msg
        self._info = info

    def getUID(self):
        return self._info['counter']

    def getFlags(self):
        flags = []
        if self._info['seen']:
            flags.append('\\Seen')
        return flags

    def getInternalDate(self):
        return rfc822.formatdate(self._info['stamp'])

    def getHeaders(self, negate, *names):
        return {'From': 'ale@incal.net',
                'To': 'me',
                'Subject': 'very important'}

    def getBodyFile(self):
        txt = self._db.get_message_body(self._info['id'])
        return StringIO.StringIO(txt)

    def getSize(self):
        return self._info['size']

    def isMultipart(self):
        return False

    def getSubPart(self, part):
        raise imap4.MailboxException('Not implemented')

