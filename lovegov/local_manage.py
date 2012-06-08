from django.core.management import execute_manager
import imp
import socket

# are we local?
LOCAL = False
if socket.getfqdn() != 'server.lovegov.com':
    LOCAL = True

try:
    imp.find_module('local_settings')
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'local_settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n" % __file__)
    sys.exit(1)

import local_settings
if __name__ == "__main__":
    execute_manager(local_settings)


