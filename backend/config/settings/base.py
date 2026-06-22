"""
Django settings for bmv3_childcare project.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables from .env file if it exists
env_path = BASE_DIR / '.env'
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ[key.strip()] = val.strip().strip('"').strip("'")


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # 3rd party
    'rest_framework',
    'django_vite',
    
    # Local apps
    'apps.core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'apps' / 'core' / 'templates'], # Added templates dir
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
# Ensure the static files from React build are found
STATICFILES_DIRS = [
    BASE_DIR / 'apps' / 'core' / 'static',
    BASE_DIR / 'apps' / 'core' / 'static' / 'react',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

# Django Vite settings
DJANGO_VITE = {
    "default": {
        "dev_mode": False,
        "dev_server_port": 5173,
        "manifest_path": str(BASE_DIR / "apps" / "core" / "static" / "react" / ".vite" / "manifest.json")
    }
}
DJANGO_VITE_ASSETS_PATH = BASE_DIR / 'apps' / 'core' / 'static' / 'react'
DJANGO_VITE_DEV_MODE = False

# Email Configuration
BREVO_API_KEY = os.environ.get('BREVO_API_KEY', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'jeremybryanvillanueva@gmail.com')

if BREVO_API_KEY:
    # Use django-anymail for Brevo HTTP API (works on PythonAnywhere free tier)
    if 'anymail' not in INSTALLED_APPS:
        INSTALLED_APPS.append('anymail')
    EMAIL_BACKEND = 'anymail.backends.sendinblue.EmailBackend'
    ANYMAIL = {
        'SENDINBLUE_API_KEY': BREVO_API_KEY,
    }
else:
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '') 
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
    if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
        # Fallback to console backend for local development if credentials aren't set
        EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    else:
        # Fallback to standard Brevo SMTP (works on local machine and paid PythonAnywhere tiers)
        EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
        EMAIL_HOST = 'smtp-relay.brevo.com'
        EMAIL_PORT = 587
        EMAIL_USE_TLS = True

# Session settings for permanent device session caching
LOGIN_URL = 'login'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
SESSION_SAVE_EVERY_REQUEST = True