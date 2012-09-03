import os
from lovegov.local_settings import *


DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     'localmirror',
        'USER':     'root',
        'PASSWORD': 'pel1ayo7val',
        'HOST':     'localhost',
        'PORT':     '3306',
        }
}
