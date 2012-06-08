from django.core.management import execute_manager
import imp

try:
    imp.find_module('live_settings')
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'live_settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n" % __file__)
    sys.exit(1)

import live_settings
if __name__ == "__main__":
    execute_manager(live_settings)