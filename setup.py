from distutils.core import setup

setup(name='cspool',
      version='0.1',
      author_email='ale@incal.net',
      packages=['cspool', 'cspool.client', 'cspool.server'],
      scripts=['bin/cspool-deliver',
               'bin/cspool-gen-keys',
               'bin/cspool-imap-server',
               'bin/cspool-server'],
      )
