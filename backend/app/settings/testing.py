from .base import *

DEBUG = TOOLBAR = TEMPLATE_DEBUG = False

NOT_TESTED_APPS = [
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'rest_framework.authtoken',
]

INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in NOT_TESTED_APPS]

ALLOWED_HOSTS = (
    'localhost',
)

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

REST_FRAMEWORK['TEST_REQUEST_DEFAULT_FORMAT'] = 'json'
