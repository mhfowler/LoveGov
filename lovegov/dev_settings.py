import settings

LOCAL = False
DEBUG = True
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = False

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
LOGGING = settings.setLogging(LOG_ROOT)

############################### EVERYTHING BELOW THE SAME ##############################################################

########################################################################################################################
#    apps, middelware, urlconf
#
########################################################################################################################

ROOT_URLCONF = settings.ROOT_URLCONF

INSTALLED_APPS = settings.INSTALLED_APPS.__add__(('south','storages','s3_folder_storage'))

MIDDLEWARE_CLASSES = settings.MIDDLEWARE_CLASSES

########################################################################################################################
#    static and media
#
########################################################################################################################
import s3_configuration
AWS_ACCESS_KEY_ID = s3_configuration.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = s3_configuration.AWS_SECRET_ACCESS_KEY
AWS_STORAGE_BUCKET_NAME = s3_configuration.AWS_STORAGE_BUCKET_NAME

DEFAULT_FILE_STORAGE = 's3_folder_storage.s3.DefaultStorage'
STATICFILES_STORAGE = 's3_folder_storage.s3.StaticStorage'

DEFAULT_S3_PATH = "media"
STATIC_S3_PATH = "static"

MEDIA_ROOT = '/%s/' % DEFAULT_S3_PATH
MEDIA_URL = 'https://%s.s3.amazonaws.com/media' % AWS_STORAGE_BUCKET_NAME
STATIC_ROOT = "/%s/" % STATIC_S3_PATH
STATIC_URL = 'https://%s.s3.amazonaws.com/static' % AWS_STORAGE_BUCKET_NAME
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

STATICFILES_DIRS = settings.STATICFILES_DIRS
STATICFILES_FINDERS = settings.STATICFILES_FINDERS

########################################################################################################################
#    templates
#
########################################################################################################################

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = settings.TEMPLATE_LOADERS

# template dirs
TEMPLATE_DIRS = settings.TEMPLATE_DIRS

########################################################################################################################
#    authentication (and integration with facebook)
#
########################################################################################################################

FACEBOOK_APP_ID = 	settings.FACEBOOK_APP_ID
FACEBOOK_APP_SECRET = 	settings.FACEBOOK_APP_SECRET

TWITTER_KEY = settings.TWITTER_KEY
TWITTER_SECRET = settings.TWITTER_SECRET

AUTH_PROFILE_MODULE = settings.AUTH_PROFILE_MODULE

AUTHENTICATION_BACKENDS = settings.AUTHENTICATION_BACKENDS

TEMPLATE_CONTEXT_PROCESSORS = settings.TEMPLATE_CONTEXT_PROCESSORS

########################################################################################################################
#    haystack and search
#
########################################################################################################################

HAYSTACK_CONNECTIONS = settings.HAYSTACK_CONNECTIONS

########################################################################################################################
#    debug toolbar
#
########################################################################################################################

DEBUG_TOOLBAR_CONFIG = {
'SHOW_TOOLBAR_CALLBACK': settings.show_toolbar,
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
#    caching
#
########################################################################################################################

# EMAIL DURING DEVELOPMENT
#EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
#EMAIL_FILE_PATH = '/log/emails'

#EMAIL DURING LIVE
EMAIL_HOST = 'smtpout.secureserver.net'
EMAIL_HOST_USER = 'team@lovegov.com'
EMAIL_HOST_PASSWORD = 'lglglgLG'
EMAIL_PORT = '25'

########################################################################################################################
#    misc settings
#
########################################################################################################################

# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = settings.TIME_ZONE

# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = settings.LANGUAGE_CODE
SITE_ID = settings.SITE_ID

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = settings.USE_I18N

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = settings.USE_L10N

# Make this unique, and don't share it with anybody.
SECRET_KEY = settings.SECRET_KEY

ADMINS = settings.ADMINS

MANAGERS = settings.MANAGERS
