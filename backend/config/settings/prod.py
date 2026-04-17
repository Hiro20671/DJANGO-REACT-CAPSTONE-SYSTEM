from .base import *
import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-in-production-random-string')

# Turn off DEBUG in production
DEBUG = False

# PythonAnywhere host format matches `yourusername.pythonanywhere.com`
# Using '*' is okay temporarily, but for strict security you can replace '*' with your PythonAnywhere domain later.
ALLOWED_HOSTS = ['*']

# Add whitenoise to middleware right after SecurityMiddleware (which is index 0)
# This serves static files efficiently in production.
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# PythonAnywhere gives safe persistent file storage, so we continue using SQLite!
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Production static settings
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

# Enable WhiteNoise compression and caching
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
