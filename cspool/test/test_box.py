import unittest
import time
from cspool.crypto import Box, generate_keys
from cspool.proto import Command, PutCommand
from cspool.server.userdb import TestUserDb
from cspool.server.deliver import encrypt_msg


class TestDeliver(unittest.TestCase):

    def setUp(self):
        self.user_sec, self.user_pub = generate_keys()
        self.spool_sec, self.spool_pub = generate_keys()

        self.userdb = TestUserDb(self.spool_sec, self.user_pub)
        self.user_box = Box('user', self.user_sec, self.spool_pub)
        self.self_box = Box('user', self.user_sec, self.user_pub)

    def test_delivery_encrypt_ok(self):
        # Test that the user can read what 'deliver.py' appends to the spool.
        msg = 'hello there'
        enc = encrypt_msg(msg, 'user', self.userdb)
        dec = Command.deserialize(
            self.user_box.decrypt(enc))
        
        self.assertEquals(msg, dec.value[0])

    def test_self_encrypt_ok(self):
        # Test that messages that we insert on the spool are readable.
        msg = 'hello there'
        cmd = PutCommand(msg)
        enc = self.self_box.encrypt(cmd.serialize())
        dec = Command.deserialize(
            self.self_box.decrypt(enc))

        self.assertEquals(msg, dec.value)
