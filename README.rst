
======
cspool
======

A proof of concept demonstrating mail delivery to a secure client via
an encrypted spool. The encrypted email archive is maintained
centrally, usually on the same infrastructure that receives inbound
email via SMTP. The spool operators do not have access to the stored
messages after they have been received.

Multiple clients can use the same encrypted spool and they will be
automatically synchronized: the (centralized) encrypted spool acts as
a coordination point.

The encrypted spool is implemented as an append-only log of serialized
commands. The client-side synchronization daemon uses the spool to
synchronize a local *message database* (currently using SQLite), which
is then made available to the user (on localhost) via the IMAP
protocol.



Installation
------------

``cspool`` requires Python 2.7 and a bunch of Python packages,
including Flask and Twisted. A more complex dependency is PyNaCl,
which itself depends on libsodium, which on most systems you'll need
to install manually from source at:

    https://github.com/jedisct1/libsodium



Running
-------

The spool server provided is meant for testing, since it lacks user
management (integration with existing user databases is left as an
exercise). To run it:

* Generate two key pairs, one for the user and one for the spool
  itself::

    $ cspool-gen-keys user.sec user.pub
    $ cspool-gen-keys spool.sec spool.pub

* Start the test spool server::

    $ cspool-server &

* Start the IMAP server::

    $ cspool-imap-server --user-key=user.sec --spool-key=spool.pub \
        --user-public-key=user.pub &

* Deliver some messages to your spool, assuming you have an email
  message in a file named ``message``::

    $ cspool-deliver --user=$USER --user-key=user.pub \
        --spool-key=spool.sec <message

* Point an IMAP client at ``localhost:1143`` and login with your
  username and an empty password.



Caveats
-------

The local message database uses the ``Message-ID`` header as the
primary key, so it is expected to be unique.

Most of the server-side plumbing isn't really implemented beyond the
proof-of-concept stage, but the interfaces are trivial and they should
be easy to adapt to any existing backend.



Todo
----

* Implement checkpoints so that the log doesn't grow forever.

* Batch updates to reduce query load on the server.
