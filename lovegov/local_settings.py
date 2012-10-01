import os
from lovegov.base_settings import *

LOCAL = True
DEBUG = True
TEMPLATE_DEBUG = True
THUMBNAIL_DEBUG = False
SHOW_TOOLBAR = False
PROFILE = False

DATABASES = {
    'default': {
         'ENGINE':  'django.db.backends.sqlite3',
        'NAME':     os.path.join(PROJECT_PATH, 'db/local.db'),
        'USER':     '',
        'PASSWORD': '',
        'HOST':     '',
        'PORT':     '',
        },
}

LOG_ROOT = "/log/"

LOGGING = setLogging(LOG_ROOT)


INSTALLED_APPS = INSTALLED_APPS.__add__(('djcelery','s3_folder_storage','storages'))


########################################################################################################################
#    debug toolbar
#
########################################################################################################################

# for django-debug-toolbar
def show_toolbar(request):
    return SHOW_TOOLBAR

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': show_toolbar,
    }

########################################################################################################################
#    caching
#
########################################################################################################################

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        }
}

########################################################################################################################
#    celery
#
########################################################################################################################
import djcelery
djcelery.setup_loader()

STATIC_URL = '/static'

THUMBNAIL_DUMMY = True

THUMBNAIL_DUMMY_SOURCE = 'http://placekitten.com/%(width)s/%(height)s'

COMPRESS_ENABLED = False

#STATICFILES_STORAGE = 'storage.CachedS3BotoStorage'


########################################################################################################################
#    email during dev
#
########################################################################################################################

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/log/emails'

#EMAIL_HOST = 'smtpout.secureserver.net'
#EMAIL_HOST_USER = 'team@lovegov.com'
#EMAIL_HOST_PASSWORD = 'lglglgLG'
#EMAIL_PORT = '25'


















