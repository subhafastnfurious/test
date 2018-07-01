from .base import *

PRODUCTION = True

# TODO: let's enable postgress here
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'not_secret',                      
        'USER': 'not_secret',
        'PASSWORD': 'not_secret',
        'HOST': 'db'
    }
}

ALLOWED_HOSTS = ['*']


STATIC_ROOT = '/var/static'
MEDIA_ROOT = '/var/media/pictures'

