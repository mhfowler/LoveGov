import os
import sys

sys.path.append('/srv/live')
sys.path.append('/srv/live/lovegov')

os.environ['DJANGO_SETTINGS_MODULE'] = 'lovegov.live_settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
