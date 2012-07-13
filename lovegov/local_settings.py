import os
from lovegov import settings

LOCAL = True
DEBUG = True
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = DEBUG
PROJECT_PATH = settings.PROJECT_PATH

DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.sqlite3',
        'NAME':     os.path.join(PROJECT_PATH, 'db/local.db'),
        'USER':      '',
        'PASSWORD':  '',
        'HOST':     '',
        'PORT':    '',
    },
}


STATIC_ROOT = settings.STATIC_ROOT

LOG_ROOT = "/log/"

LOGGING = settings.setLogging(LOG_ROOT)

########################################################################################################################
#    apps, middelware, urlconf
#
########################################################################################################################

ROOT_URLCONF = settings.ROOT_URLCONF

INSTALLED_APPS = settings.INSTALLED_APPS

MIDDLEWARE_CLASSES = settings.MIDDLEWARE_CLASSES

########################################################################################################################
#    static and media
#
########################################################################################################################

# URL prefix for static files.
STATIC_URL = settings.STATIC_URL

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = settings.MEDIA_ROOT

# URL that handles the media served from MEDIA_ROOT. Make sure to use a trailing slash.
MEDIA_URL =  settings.MEDIA_URL

# URL prefix for admin static files -- CSS, JavaScript and images. Make sure to use a trailing slash.
ADMIN_MEDIA_PREFIX = settings.ADMIN_MEDIA_PREFIX

# Additional locations of static files
STATICFILES_DIRS = settings.STATICFILES_DIRS

# List of finder classes that know how to find static files in various locations.
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
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/log/emails'

# EMAIL
# EMAIL_HOST = 'smtpout.secureserver.net'
# EMAIL_HOST_USER = 'team@lovegov.com'
# EMAIL_HOST_PASSWORD = 'freeGOV'
# EMAIL_PORT = '25'

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


