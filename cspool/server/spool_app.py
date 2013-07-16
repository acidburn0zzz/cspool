# A reference implementation of the spool server API.
#
# This is nothing more than a toy due to the lack of authentication
# and proper error checking.

import json
import optparse
from flask import Flask, request, make_response
from cspool.server.spool import Spool


app = Flask(__name__)


def b64encode_or_none(s):
    if s is None:
        return s
    return s.encode('base64')


@app.route('/scan')
def handle_scan():
    spool = Spool(request.args['user'])
    start_pos = int(request.args['start_pos'])
    out = [{'pos': pos, 'entry': b64encode_or_none(entry)}
           for pos, entry in spool.scan(start_pos)]
    response = make_response(json.dumps(out))
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/command', methods=('POST',))
def handle_command():
    spool = Spool(request.form['user'])
    cmd_data = bytes(request.form['encrypted_command']).decode('base64')
    spool.append(cmd_data)
    return 'ok'


def main():
    parser = optparse.OptionParser()
    parser.add_option('--port', type='int', default=3999)
    parser.add_option('--debug', default=False, action='store_true')
    parser.add_option('--spool-dir', dest='spool_root', default='./spool',
                      help='Spool base path')
    opts, args = parser.parse_args()

    Spool.SPOOL_ROOT = opts.spool_root

    app.debug = opts.debug
    app.run('127.0.0.1', opts.port)


if __name__ == '__main__':
    main()

    
