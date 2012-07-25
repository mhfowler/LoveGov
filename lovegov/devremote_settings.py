import os
from lovegov import local_settings as local

LOCAL = local.LOCAL
DEBUG = local.DEBUG
SHOW_TOOLBAR = local.SHOW_TOOLBAR
TEMPLATE_DEBUG = True
THUMBNAIL_DEBUG = False
PROJECT_PATH = local.PROJECT_PATH

DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     'lgdb',
        'USER':     'root',
        'PASSWORD': 'lglglg12',
        'HOST':     'lgdbinstance.cssrhulnfuuk.us-east-1.rds.amazonaws.com',
        'PORT':     '3306',
        }
    }

STATIC_ROOT = local.STATIC_ROOT

LOGGING = local.LOGGING

########################################################################################################################
#    apps, middelware, urlconf
#
########################################################################################################################

ROOT_URLCONF = local.ROOT_URLCONF

INSTALLED_APPS = local.INSTALLED_APPS.__add__(('south',))

MIDDLEWARE_CLASSES = local.MIDDLEWARE_CLASSES

########################################################################################################################
#    static and media
#
########################################################################################################################

# URL prefix for static files.
STATIC_URL = local.STATIC_URL

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = local.MEDIA_ROOT

# URL that handles the media served from MEDIA_ROOT. Make sure to use a trailing slash.
MEDIA_URL =  local.MEDIA_URL

# URL prefix for admin static files -- CSS, JavaScript and images. Make sure to use a trailing slash.
ADMIN_MEDIA_PREFIX = local.ADMIN_MEDIA_PREFIX

# Additional locations of static files
STATICFILES_DIRS = local.STATICFILES_DIRS

# List of finder classes that know how to find static files in various locations.
STATICFILES_FINDERS = local.STATICFILES_FINDERS

########################################################################################################################
#    templates
#
########################################################################################################################

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = local.TEMPLATE_LOADERS

# template dirs
TEMPLATE_DIRS = local.TEMPLATE_DIRS

########################################################################################################################
#    authentication (and integration with facebook)
#
########################################################################################################################

FACEBOOK_APP_ID = 	local.FACEBOOK_APP_ID
FACEBOOK_APP_SECRET = 	local.FACEBOOK_APP_SECRET

TWITTER_KEY = local.TWITTER_KEY
TWITTER_SECRET = local.TWITTER_SECRET

AUTH_PROFILE_MODULE = local.AUTH_PROFILE_MODULE

AUTHENTICATION_BACKENDS = local.AUTHENTICATION_BACKENDS

TEMPLATE_CONTEXT_PROCESSORS = local.TEMPLATE_CONTEXT_PROCESSORS

########################################################################################################################
#    haystack and search
#
########################################################################################################################

HAYSTACK_CONNECTIONS = local.HAYSTACK_CONNECTIONS

########################################################################################################################
#    debug toolbar
#
########################################################################################################################

DEBUG_TOOLBAR_CONFIG = local.DEBUG_TOOLBAR_CONFIG

########################################################################################################################
#    caching
#
########################################################################################################################

CACHES = local.CACHES

########################################################################################################################
#    email
#
########################################################################################################################

EMAIL_BACKEND = local.EMAIL_BACKEND
EMAIL_FILE_PATH = local.EMAIL_FILE_PATH

########################################################################################################################
#    misc settings
#
########################################################################################################################

# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = local.TIME_ZONE

# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = local.LANGUAGE_CODE
SITE_ID = local.SITE_ID

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = local.USE_I18N

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = local.USE_L10N

# Make this unique, and don't share it with anybody.
SECRET_KEY = local.SECRET_KEY

ADMINS = local.ADMINS

MANAGERS = local.MANAGERS


