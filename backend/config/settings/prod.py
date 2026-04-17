from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'change-this-in-production'

DEBUG = False

ALLOWED_HOSTS = ['your-production-domain.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Production static settings
STATIC_ROOT = BASE_DIR / 'staticfiles'
