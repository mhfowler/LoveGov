import os
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
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
    'django_extensions',
    'compressor',

    # internal
    'lovegov.modernpolitics',
    'lovegov.frontend',
    'lovegov.tests'
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
STATIC_URL_NOSLASH = '/static'

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
    'compressor.finders.CompressorFinder',
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
LOG_ROOT = '/log/'

def setLogging(log_root):
    return {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'verbose': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            }
        },
        'handlers': {
            'null': {
                'level': 'DEBUG',
                'class': 'django.utils.log.NullHandler',
                },
            'lg_critical_handler': {
                'level':'CRITICAL',
                'class':'logging.handlers.RotatingFileHandler',
                'filename': log_root + 'critical.log',
                'maxBytes': 1024*1024*5, # 5 MB
                'backupCount': 5,
                'formatter':'verbose',
                },
            'lg_error_handler': {
                'level':'CRITICAL',
                'class':'logging.handlers.RotatingFileHandler',
                'filename': log_root + 'error.log',
                'maxBytes': 1024*1024*5, # 5 MB
                'backupCount': 5,
                'formatter':'verbose',
                },
            'lg_warning_handler': {
                'level':'WARNING',
                'class':'logging.handlers.RotatingFileHandler',
                'filename': log_root + 'warning.log',
                'maxBytes': 1024*1024*5, # 5 MB
                'backupCount': 5,
                'formatter':'verbose',
                },
            'lg_info_handler': {
                'level':'INFO',
                'class':'logging.handlers.RotatingFileHandler',
                'filename': log_root + 'info.log',
                'maxBytes': 1024*1024*5, # 5 MB
                'backupCount': 5,
                'formatter':'verbose',
                },
            'lg_debug_handler': {
                'level':'DEBUG',
                'class':'logging.handlers.RotatingFileHandler',
                'filename': log_root + 'debug.log',
                'maxBytes': 1024*1024*5, # 5 MB
                'backupCount': 5,
                'formatter':'verbose',
                },
            'mail_admins': {
                'class': 'django.utils.log.AdminEmailHandler',
                'level': 'ERROR',
                'include_html': True,
                },
            'scheduled_handler': {
                'level':'DEBUG',
                'class':'logging.handlers.RotatingFileHandler',
                'filename': log_root + 'scheduled.log',
                'maxBytes': 1024*1024*5, # 5 MB
                'backupCount': 5,
                'formatter':'verbose',
                },
            'browser_handler': {
                'level':'DEBUG',
                'class':'logging.handlers.RotatingFileHandler',
                'filename': log_root + 'browser.log',
                'maxBytes': 1024*1024*5, # 5 MB
                'backupCount': 5,
                'formatter':'verbose',
                },
            },
        'loggers': {
            'django': {
                'handlers': ['null'],
                'propagate': True,
                'level': 'DEBUG',
                },
            'django.request': {
                'handlers': ['mail_admins'],
                'level': 'ERROR',
                'propagate': True,
                },
            'lg.critical': {
                'handlers': ['lg_critical_handler'],
                'level': 'CRITICAL',
                'propagate': True,
                },
            'lg.error': {
                'handlers': ['lg_error_handler'],
                'level': 'ERROR',
                'propagate': True,
            },
            'lg.warning': {
                'handlers': ['lg_warning_handler'],
                'level': 'WARNING',
                'propagate': True,
                },
            'lg.info': {
                'handlers': ['lg_info_handler'],
                'level': 'INFO',
                'propagate': True,
                },
            'lg.debug': {
                'handlers': ['lg_debug_handler'],
                'level': 'DEBUG',
                'propagate': True,
                },
            'scheduledlogger': {
                'handlers': ['scheduled_handler'],
                'level': 'DEBUG',
                'propagate': False
            },
            'browserlogger': {
                'handlers': ['browser_handler'],
                'level': 'DEBUG',
                'propagate': False
            },
        }
    }

LOGGING = setLogging(LOG_ROOT)

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

BROKER_URL = 'librabbitmq://guest:guest@localhost:5672/'

########################################################################################################################
#    email
#
########################################################################################################################

#EMAIL DURING LIVE
#EMAIL_USE_TLS = True
#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_HOST_USER = 'team@lovegov.com'
#EMAIL_HOST_PASSWORD = 'freeGOV2'
#EMAIL_PORT = 587

########################################################################################################################
#   testing
#
########################################################################################################################
FIXTURE_DIRS = os.path.join(PROJECT_PATH, 'tests/fixtures')

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
    ('Jeremy Greenfield', 'jsgreenf@gmail.com'),
    )

MANAGERS = ADMINS

SERVER_EMAIL = 'team@lovegov.com'

import s3_configuration
AWS_ACCESS_KEY_ID = s3_configuration.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = s3_configuration.AWS_SECRET_ACCESS_KEY
AWS_STORAGE_BUCKET_NAME = s3_configuration.AWS_STORAGE_BUCKET_NAME

EMAIL_BACKEND = 'django_ses.SESBackend'

########################################## ANALYTICS SETTINGS #########################################################


CURRENT_TEST_RUN = 0

BENCHMARK_PAGES = ['/home/', '/groups/', '/elections/', '/questions/']

BENCHMARK_AJAX = [
    ('/home/', 'getFeed'),
    ('/groups/', 'getGroups')
]