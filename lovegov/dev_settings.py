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
#    static and media
#
########################################################################################################################

USE_S3 = False

if USE_S3:
    DEFAULT_FILE_STORAGE = 's3_folder_storage.s3.DefaultStorage'
    STATICFILES_STORAGE = 's3_folder_storage.s3.StaticStorage'

    DEFAULT_S3_PATH = "media"
    STATIC_S3_PATH = "static"

    MEDIA_ROOT = '/%s/' % DEFAULT_S3_PATH
    MEDIA_URL = 'https://%s.s3.amazonaws.com/media' % AWS_STORAGE_BUCKET_NAME
    STATIC_ROOT = "/%s/" % STATIC_S3_PATH
    STATIC_URL = 'https://%s.s3.amazonaws.com/static' % AWS_STORAGE_BUCKET_NAME
    ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

    from compressor_settings import *
    COMPRESS_ENABLED = False

else:
    # URL prefix for static files.
    STATIC_URL = '/static/'
    MEDIA_URL =  MEDIA_URL
    from compressor_settings import *
    COMPRESS_URL = "/fake/"
    COMPRESS_ENABLED = False


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
COMPRESS_OUTPUT_DIR = 'CACHE' # default, included for simplicity
COMPRESS_STORAGE = 'storage.CachedS3BotoStorage'
#COMPRESS_STORAGE = 'compressor.storage.CompressorFileStorage'
COMPRESS_ROOT = "LoveGov/frontend"

COMPRESS_ENABLED = True

ABSOLUTE_STATIC_URL_NOSLASH = "http://dev.lovegov.com" + STATIC_URL_NOSLASH