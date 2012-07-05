import os
PROJECT_PATH = os.path.dirname(__file__)
DEBUG = False
UPDATE = False
SHOW_TOOLBAR = False



########################################################################################################################
#    apps, middelware, urlconf
#
########################################################################################################################

ROOT_URLCONF = 'lovegov.urls'

INSTALLED_APPS = (

    # django
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # apps
    'haystack',
    'sorl.thumbnail',
    'debug_toolbar',

    # internal
    'lovegov.modernpolitics',
    'lovegov.frontend',
    'django_extensions'

    )

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware'
    )

########################################################################################################################
#    static and media
#
########################################################################################################################

# different projects will use different root
STATIC_ROOT = '/static/'

# URL prefix for static files.
STATIC_URL = '/static/'

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = '/media/'              # !!!!

# URL that handles the media served from MEDIA_ROOT. Make sure to use a trailing slash.
MEDIA_URL =  '/media/'

# URL prefix for admin static files -- CSS, JavaScript and images. Make sure to use a trailing slash.
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, 'frontend/static').replace('\\','/'),
    )

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    )

########################################################################################################################
#    templates
#
########################################################################################################################

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
    )

# template dirs
TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'alpha/templates').replace('\\','/'),
    )

########################################################################################################################
#    authentication (and integration with facebook and twitter)
#
########################################################################################################################

FACEBOOK_APP_ID = 	'184966154940334'
FACEBOOK_APP_SECRET = 	'0ec0b8b37633508361584510db53a6dc'

TWITTER_KEY = 'kb6Hop3poGH4Ocb0bJUgw'
TWITTER_SECRET = 'MWHKY9onFg9ZMX5lOtEyLJWsAkCMNqRAXBo9dS3Iw'

AUTH_PROFILE_MODULE = 'modernpolitics.UserProfile'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    )

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    )

########################################################################################################################
#    haystack and search
#
########################################################################################################################

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE' : 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'modernpolitics/search_indexes')
    }
}

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
#    logging (different settings use different logging)
#
########################################################################################################################
LOGGING = {      # !!!!!
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        },
    'handlers': {
        'default': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/log/default.log',
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter':'standard',
            },
        'request_handler': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/log/django_request.log',
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter':'standard',
            },
        'file_handler': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/log/django.log',
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter':'standard',
            },
        'scheduled_handler': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/log/scheduled.log',
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter':'standard',
            },
        },
    'loggers': {

        '': {
            'handlers': ['default'],
            'level': 'ERROR',
            'propagate': True
        },
        'django.request': { # Stop SQL debug from logging to main logger
                            'handlers': ['request_handler'],
                            'level': 'DEBUG',
                            'propagate': False
        },
        'filelogger': {
            'handlers': ['file_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
        'scheduledlogger': {
            'handlers': ['scheduled_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
        }
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
EMAIL_HOST_PASSWORD = 'freeGOV'
EMAIL_PORT = '25'

########################################################################################################################
#    misc settings
#
########################################################################################################################

# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = 'America/New_York'

# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'
SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'uodf#%)e0gss8zbqnnfqj=ppbi!*4n_ss0joum-_udavihl6m%'

ADMINS = (
    ('Max Fowler', 'max_fowler@brown.edu'),
    ('Clay Dunwell','clayton_dunwell@brown.edu'),
    ('Jonathan Koh', 'jonathanvkoh@gmail.com'),
    ('Jeremy Greenfield', 'jsgreenf@gmail.com'),
    )

MANAGERS = ADMINS

