
from dev_settings import *
import base_settings

DEBUG = False
TEMPLATE_DEBUG = False
THUMBNAIL_DEBUG = False

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
LOGGING = base_settings.setLogging(LOG_ROOT)

