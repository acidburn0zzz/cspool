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

    def __init__(self, private_key, public_key):
        self._private_key = private_key
        self._public_key = public_key

    def get_cryptobox(self, user):
        return crypto.Box(user, self._private_key, self._public_key)

