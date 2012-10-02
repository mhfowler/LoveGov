import os
from lovegov.local_settings import *


DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     'lglive',
        'USER':     'root',
        'PASSWORD': 'lglglg12',
        'HOST':     'lgdbinstance.cssrhulnfuuk.us-east-1.rds.amazonaws.com',
        'PORT':     '3306',
        }
}


