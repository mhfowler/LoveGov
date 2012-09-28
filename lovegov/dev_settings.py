from base_settings import *

LOCAL = False
DEBUG = True
TEMPLATE_DEBUG = True
THUMBNAIL_DEBUG = False
SHOW_TOOLBAR = False
PROFILE = True

############################### DIFFERENCE BETWEEN LIVE AND DEV ########################################################

DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     'lgdb',
        'USER':     'root',
        'PASSWORD': 'lglglg12',
        'HOST':     'lgdbinstance.cssrhulnfuuk.us-east-1.rds.amazonaws.com',
        'PORT':     '3306',
    },
    'live': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     'lglive',
        'USER':     'root',
        'PASSWORD': 'lglglg12',
        'HOST':     'lgdbinstance.cssrhulnfuuk.us-east-1.rds.amazonaws.com',
        'PORT':     '3306',
        },
}

STATIC_ROOT = '/static/dev/'
MEDIA_ROOT = '/media/dev/'
LOG_ROOT = "/log/dev/"
PROFILE_LOG_BASE = "/log/dev/profiles/"
LOGGING = setLogging(LOG_ROOT)

INSTALLED_APPS = INSTALLED_APPS.__add__(('south',
                                                  'storages',
                                                  's3_folder_storage',
                                                  'djcelery',))


########################################################################################################################
#    debug toolbar
#
########################################################################################################################

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


COMPRESS_URL = STATIC_URL
#COMPRESS_STORAGE = 'storage.CachedS3BotoStorage'
COMPRESS_STORAGE = 'compressor.storage.CompressorFileStorage'
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_OUTPUT_DIR = 'CACHE' # default, included for simplicity

COMPRESS_ENABLED = True

ABSOLUTE_STATIC_URL_NOSLASH = "http://dev.lovegov.com" + STATIC_URL_NOSLASH