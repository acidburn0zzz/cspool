import json
import urllib
import urllib2


class Error(Exception):
    pass


class ServerStub(object):
    """Stub for a remote spool server, accessed via HTTP."""

    def __init__(self, url, user):
        self._url = url.rstrip('/')
        self._user = user

    def scan(self, start_pos):
        qstr = urllib.urlencode({'user': self._user, 'start_pos': str(start_pos)})
        resp = urllib2.urlopen('%s/scan?%s' % (self._url, qstr))
        for entry in json.loads(resp.read()):
            yield entry['pos'], entry['entry']

    def send_command(self, encrypted_command):
        data = {'user': self._user,
                'encrypted_command': encrypted_command}
        req = urllib2.Request(self._url + '/command', data=data)
        resp = urllib2.urlopen(req)
        if resp.code != 200:
            raise Error('send_command http status %d' % resp.code)

