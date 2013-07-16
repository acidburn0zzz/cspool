import os
import fcntl
import contextlib
import struct


class Error(Exception):
    pass


@contextlib.contextmanager
def flock(path):
    with open(path, 'r+') as fd:
        fcntl.lockf(fd, fcntl.LOCK_EX)
        yield
        fcntl.lockf(fd, fcntl.LOCK_UN)


def logread(fd):
    pos = fd.tell()
    szbuf = fd.read(4)
    if not szbuf:
        return pos, None
    sz = struct.unpack('i', szbuf)[0]
    data = fd.read(sz)
    if len(data) != sz:
        print 'short read, log truncated'
        return pos, None
    return pos, data


def logwrite(entry, fd):
    pos = fd.tell()
    fd.write(struct.pack('i', len(entry)))
    fd.write(entry)
    return pos


class Spool(object):
    """Spool implementation (file-based)."""

    SPOOL_ROOT = './spool'

    def __init__(self, user):
        self._root = os.path.join(self.SPOOL_ROOT, user)
        if not os.path.isdir(self._root):
            os.makedirs(self._root)
        self._lock_file_path = os.path.join(self._root, 'lock')
        self._log_file_path = os.path.join(self._root, 'log')

    def scan(self, start_pos=0):
        """Scan the log for entries starting at 'start_pos'.

        Yields (pos, entry) tuples. The final tuple has entry = None,
        signaling the end of the log.
        """
        with open(self._log_file_path, 'r') as fd:
            fd.seek(0, 2)
            end_pos = fd.tell()

            if start_pos >= end_pos:
                return

            fd.seek(start_pos, 0)
            while True:
                pos, entry = logread(fd)
                yield pos, entry
                if entry is None:
                    break

    def append(self, entry):
        """Append an entry to the log.

        Returns the log position of the entry.
        """
        with open(self._log_file_path, 'a') as fd:
            return logwrite(entry, fd)

