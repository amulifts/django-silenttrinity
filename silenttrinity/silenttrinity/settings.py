# silenttrinity/silenttrinity/silenttrinity/settings.py

"""
Django settings for silenttrinity project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# /home/parallels/Downloads/asilenttrinity/silenttrinity/silenttrinity


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-io$=ik*o#3vod^egct1z#f2zoq_1qs*+ju8@-+v5e&yl_#x3#%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'teamserver',
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

ROOT_URLCONF = 'silenttrinity.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'silenttrinity.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# WebSocket settings
WEBSOCKET_HOST = '0.0.0.0'
WEBSOCKET_PORT = 5000

# Custom user model
AUTH_USER_MODEL = 'teamserver.TeamServerUser'

# Add teamserver to INSTALLED_APPS
if 'teamserver' not in INSTALLED_APPS:
    INSTALLED_APPS.append('teamserver')

# Token expiration time in hours
TOKEN_EXPIRATION_HOURS = 24

# TeamServer settings
TEAMSERVER = {
    'HOST': '0.0.0.0',
    'PORT': 5000,
    'SSL': False,
    'CERT_PATH': None,
    'KEY_PATH': None,
}

import os

C2_LOG_DIR = os.path.join(BASE_DIR, 'silenttrinity', 'silenttrinity', 'logs')

# Set the environment variable
os.environ['C2_LOG_DIR'] = C2_LOG_DIR

# Ensure the directory exists
os.makedirs(C2_LOG_DIR, exist_ok=True)

import zmq

# Define a function to generate keys
def generate_zmq_keys():
    """Generate a CurveZMQ key pair and return the public and secret keys."""
    public_key, secret_key = zmq.curve_keypair()
    return public_key.decode(), secret_key.decode()

# Check if ZMQ keys are already set in the environment
ZMQ_SERVER_PUBLIC_KEY = os.getenv('ZMQ_SERVER_PUBLIC_KEY')
ZMQ_SERVER_SECRET_KEY = os.getenv('ZMQ_SERVER_SECRET_KEY')

if not ZMQ_SERVER_PUBLIC_KEY or not ZMQ_SERVER_SECRET_KEY:
    # Generate new keys if not already set
    ZMQ_SERVER_PUBLIC_KEY, ZMQ_SERVER_SECRET_KEY = generate_zmq_keys()

    # Optionally save the generated keys to environment variables for future use
    os.environ['ZMQ_SERVER_PUBLIC_KEY'] = ZMQ_SERVER_PUBLIC_KEY
    os.environ['ZMQ_SERVER_SECRET_KEY'] = ZMQ_SERVER_SECRET_KEY

# Log the keys (for debugging only; avoid in production)
# print(f"ZMQ_SERVER_PUBLIC_KEY: {ZMQ_SERVER_PUBLIC_KEY}")
# print(f"ZMQ_SERVER_SECRET_KEY: {ZMQ_SERVER_SECRET_KEY}")

# WebSocket TLS/SSL settings
WEBSOCKET_CERT_PATH = os.path.join(BASE_DIR, 'silenttrinity', 'silenttrinity', 'server.crt')
WEBSOCKET_KEY_PATH = os.path.join(BASE_DIR, 'silenttrinity', 'silenttrinity', 'server.key')
