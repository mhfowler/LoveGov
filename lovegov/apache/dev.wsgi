import os
import sys

sys.path.append('/srv/dev')
sys.path.append('/srv/dev/lovegov')

os.environ['DJANGO_SETTINGS_MODULE'] = 'lovegov.dev_settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
