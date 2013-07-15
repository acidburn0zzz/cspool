import logging
import struct
import threading

from cspool.crypto import decrypt
from cspool.proto import Command

log = logging.getLogger(__name__)


class Syncer(threading.Thread):

    PERIOD = 300

    def __init__(self, db, server, key):
        threading.Thread.__init__(self)
        self._db = db
        self._server = server
        self._key = key
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()
        self.join()

    def _read_pos(self):
        try:
            return self._db.get_sync_state()
        except:
            return 0

    def _write_pos(self, pos):
        self._db.set_sync_state(pos)

    def _scan(self):
        cur_pos = self._read_pos()
        try:
            for pos, entry in self._server.scan(cur_pos):
                cur_pos = pos
                if not entry:
                    continue
                try:
                    cmd = Command.deserialize(decrypt(self._key, entry))
                    cmd.apply(self._db)
                except Exception, e:
                    log.exception('error in apply(), skipping record...')
        finally:
            self._write_pos(cur_pos)

    def run(self):
        while not self._stop_event.is_set():
            try:
                self._scan()
            except Exception, e:
                log.exception('scan() failed: %s', e)
            self._stop_event.wait(self.PERIOD)
