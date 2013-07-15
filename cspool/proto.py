# The local message database is implemented as a very simple key/value
# store, where the keys are message IDs (assumed unique).
# The write operations available on it are:
#
# Put(message)
# SetFlag(message-id)
# Expunge()
# Checkpoint()
#
# Each operation is represented as a Command that can be serialized
# and stored in the Spool. The Spool itself is just a single,
# append-only log of operations. Since the log is centrally
# maintained, the various clients do not need to perform any special
# synchronization between themselves.

import abc
import pickle


class Command(object):
    """A serializable operation that modifies state.

    Each command contains a single 'value' attribute. Use standard
    Python containers to pass multiple values (objects have to be
    pickle-safe).
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, value):
        self.value = value

    @abc.abstractmethod
    def apply(self, db):
        pass

    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(data):
        return pickle.loads(data)


class PutCommand(Command):

    def apply(self, db):
        message, timestamp = self.value
        db.add_message(message, timestamp)


class ExpungeCommand(Command):

    def apply(self, db):
        db.expunge()


class SetFlag(Command):

    def apply(self, db):
        message_id, flag, value = self.value
        db.set_flag_on_message(message_id, flag, value)
