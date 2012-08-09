import os
from lovegov import base_settings

LOCAL = True
DEBUG = True
SHOW_TOOLBAR = False
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = DEBUG
PROJECT_PATH = base_settings.PROJECT_PATH

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

STATIC_ROOT = base_settings.STATIC_ROOT

LOG_ROOT = "/log/"

LOGGING = base_settings.setLogging(LOG_ROOT)

########################################################################################################################
#    apps, middelware, urlconf
#
########################################################################################################################

ROOT_URLCONF = base_settings.ROOT_URLCONF

INSTALLED_APPS = base_settings.INSTALLED_APPS.__add__(('south','djcelery','s3_folder_storage','storages'))

MIDDLEWARE_CLASSES = base_settings.MIDDLEWARE_CLASSES

########################################################################################################################
#    static and media
#
########################################################################################################################

# URL prefix for static files.
STATIC_URL = base_settings.STATIC_URL

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = base_settings.MEDIA_ROOT

# URL that handles the media served from MEDIA_ROOT. Make sure to use a trailing slash.
MEDIA_URL =  base_settings.MEDIA_URL

# URL prefix for admin static files -- CSS, JavaScript and images. Make sure to use a trailing slash.
ADMIN_MEDIA_PREFIX = base_settings.ADMIN_MEDIA_PREFIX

# Additional locations of static files
STATICFILES_DIRS = base_settings.STATICFILES_DIRS

# List of finder classes that know how to find static files in various locations.
STATICFILES_FINDERS = base_settings.STATICFILES_FINDERS

########################################################################################################################
#    templates
#
########################################################################################################################

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = base_settings.TEMPLATE_LOADERS

# template dirs
TEMPLATE_DIRS = base_settings.TEMPLATE_DIRS

########################################################################################################################
#    authentication (and integration with facebook)
#
########################################################################################################################

FACEBOOK_APP_ID = 	base_settings.FACEBOOK_APP_ID
FACEBOOK_APP_SECRET = 	base_settings.FACEBOOK_APP_SECRET

TWITTER_KEY = base_settings.TWITTER_KEY
TWITTER_SECRET = base_settings.TWITTER_SECRET

AUTH_PROFILE_MODULE = base_settings.AUTH_PROFILE_MODULE

AUTHENTICATION_BACKENDS = base_settings.AUTHENTICATION_BACKENDS

TEMPLATE_CONTEXT_PROCESSORS = base_settings.TEMPLATE_CONTEXT_PROCESSORS

########################################################################################################################
#    haystack and search
#
########################################################################################################################

HAYSTACK_CONNECTIONS = base_settings.HAYSTACK_CONNECTIONS

########################################################################################################################
#    debug toolbar
#
########################################################################################################################

# for django-debug-toolbar
def show_toolbar(request):
    from lovegov.modernpolitics.helpers import getUserProfile
    if DEBUG and SHOW_TOOLBAR:
        user_prof = getUserProfile(request)
        if user_prof:
            if user_prof.developer:
                return True
    return False

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

BROKER_URL = base_settings.BROKER_URL

########################################################################################################################
#    email
#
########################################################################################################################

# EMAIL DURING DEVELOPMENT
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/log/emails'

########################################################################################################################
#   testing
#
########################################################################################################################
FIXTURE_DIRS = base_settings.FIXTURE_DIRS

########################################################################################################################
#    misc settings
#
########################################################################################################################

# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = base_settings.TIME_ZONE

# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = base_settings.LANGUAGE_CODE
SITE_ID = base_settings.SITE_ID

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = base_settings.USE_I18N

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = base_settings.USE_L10N

# Make this unique, and don't share it with anybody.
SECRET_KEY = base_settings.SECRET_KEY

ADMINS = base_settings.ADMINS

MANAGERS = base_settings.MANAGERS

import s3_configuration
AWS_ACCESS_KEY_ID = s3_configuration.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = s3_configuration.AWS_SECRET_ACCESS_KEY
AWS_STORAGE_BUCKET_NAME = s3_configuration.AWS_STORAGE_BUCKET_NAME

DEFAULT_FILE_STORAGE = 's3_folder_storage.s3.DefaultStorage'
STATICFILES_STORAGE = 'storage.CachedS3BotoStorage'

DEFAULT_S3_PATH = "media"
STATIC_S3_PATH = "static"

COMPRESS_ENABLED = False

COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter', 
                        'compressor.filters.cssmin.CSSMinFilter',
                        'compressor.filters.template.TemplateFilter']


COMPRESS_URL = 'https://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
COMPRESS_OUTPUT_DIR = 'CACHE' # default, included for simplicity
COMPRESS_STORAGE = STATICFILES_STORAGE

STATIC_URL = '/static/'
COMPRESS_ROOT = "frontend"
print STATIC_URL
