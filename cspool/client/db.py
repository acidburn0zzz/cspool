import email
import json
import sqlite3
import os
import contextlib
import threading


class Error(Exception):
    pass


@contextlib.contextmanager
def commit(conn):
    yield conn.cursor()
    conn.commit()


@contextlib.contextmanager
def rollback(conn):
    yield conn.cursor()
    conn.rollback()


class Database(object):
    """Local database (using SQLite).

    Run with sqlcrypt if you want encryption.
    """

    def __init__(self, dbpath):
        self._dbpath = dbpath
        self._local = threading.local()
        if not os.path.exists(dbpath):
            c = self._conn().cursor()
            c.execute('create table sync_state (pos integer)')
            c.execute('insert into sync_state values (0)')
            c.execute('create table messages (id varchar(255) primary key, seen integer default 0, deleted integer default 0, stamp integer, size integer, headers text, body text)')
            c.execute('create unique index messageid on messages (id)')
            self._conn().commit()

    def _conn(self):
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(self._dbpath)
        return self._local.conn

    def get_sync_state(self):
        with rollback(self._conn()) as c:
            c.execute('select pos from sync_state')
            return int(c.fetchone()[0])

    def set_sync_state(self, pos):
        with commit(self._conn()) as c:
            c.execute('update sync_state set pos = ?', (pos,))

    def add_message(self, msg_text, timestamp):
        msg = email.message_from_string(msg_text)
        size = len(msg_text)
        msgid = msg['Message-Id']
        headers, body = msg_text.split('\r\n\r\n', 1)
        with commit(self._conn()) as c:
            c.execute('insert into messages(id, stamp, size, headers, body) values(?, ?, ?, ?, ?)',
                      (msgid, timestamp, size, headers, body))

    def delete_message(self, msgid):
        raise NotImplementedError()

    def set_flag_on_message(self, msgid, flag, value):
        if flag not in ('seen', 'deleted'):
            raise Error('unknown flag "%s"' % flag)
        with commit(self._conn()) as c:
            c.execute('update messages set %s = ? where id = ?' % flag,
                      (msgid, int(value)))

    def expunge(self):
        with commit(self._conn()) as c:
            c.execute('delete from messages where deleted = 1')

    def to_expunge(self):
        with rollback(self._conn()) as c:
            c.execute('select id from messages where deleted = 1')
            return [x[0] for x in c.fetchall()]

    def count_messages(self, unread=False):
        with rollback(self._conn()) as c:
            sql = 'select count(*) from messages'
            if unread:
                sql += ' where seen = 0'
            c.execute(sql)
            return c.fetchone()[0]

    def get_message_body(self, msgid):
        with rollback(self._conn()) as c:
            c.execute('select body from messages where id = ?', (msgid,))
            return c.fetchone()[0]

    def fetch_headers(self, messages=None):
        print 'fetch_headers():', messages
        with rollback(self._conn()) as c:
            if messages:
                # Boo! This won't really escape message IDs properly...
                c.execute('select id, seen, deleted, stamp, size, headers from messages where id in (?) order by id', (','.join(messages),))
            else:
                c.execute('select id, seen, deleted, stamp, size, headers from messages order by id')
            while True:
                row = c.fetchone()
                if not row:
                    break
                yield ({'id': row[0],
                        'seen': row[1],
                        'deleted': row[2],
                        'stamp': row[3],
                        'size': row[4]},
                       email.message_from_string(row[5]))
