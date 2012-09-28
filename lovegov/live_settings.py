
from dev_settings import *
import base_settings

DEBUG = False
TEMPLATE_DEBUG = False
THUMBNAIL_DEBUG = False
SHOW_TOOLBAR = False
PROFILE = False

############################### DIFFERENCE BETWEEN LIVE AND DEV ########################################################

DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     'lglive',
        'USER':     'root',
        'PASSWORD': 'lglglg12',
        'HOST':     'lgdbinstance.cssrhulnfuuk.us-east-1.rds.amazonaws.com',
        'PORT':     '3306',
        },
}

STATIC_ROOT = '/static/live/'
MEDIA_ROOT = '/media/live/'
LOG_ROOT = "/log/live/"
PROFILE_LOG_BASE = "/log/live/profiles/"
LOGGING = base_settings.setLogging(LOG_ROOT)

ADMIN_MEDIA_PREFIX = STATIC_ROOT + "admin/"

COMPRESS_URL = STATIC_URL
COMPRESS_OUTPUT_DIR = 'CACHE' # default, included for simplicity
COMPRESS_STORAGE = 'storage.CachedS3BotoStorage'
#COMPRESS_STORAGE = 'compressor.storage.CompressorFileStorage'
COMPRESS_ROOT = "LoveGov/frontend"

COMPRESS_ENABLED = False

ABSOLUTE_STATIC_URL_NOSLASH = "http://dev.lovegov.com" + STATIC_URL_NOSLASH