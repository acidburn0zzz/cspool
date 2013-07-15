import abc
from cspool import crypto


class UserDb(object):

    __metaclas__ = abc.ABCMeta

    @abc.abstractmethod
    def get_cryptobox(self, user):
        """Return a crypto.Box that will encrypt data for this user."""
        pass


class TestUserDb(UserDb):
    """A userdb implementation that serves the same key for everyone.

    This is only useful for testing.
    """

    def __init__(self, user_public_key_file, spool_private_key_file):
        with open(user_public_key_file) as fd:
            self._public_key = fd.read()
        with open(spool_private_key_file) as fd:
            self._private_key = fd.read()

    def get_cryptobox(self, user):
        return crypto.Box(user, self._private_key, self._public_key)

