import os
from pathlib import Path

from split_settings.tools import include
from todo.settings_components.main_config import main_config, REDIS_URL


include(
    'settings_components/db_config.py',
    'settings_components/locale_config.py',
    'settings_components/rest_config.py',
    'settings_components/celery_config.py',
    'settings_components/templates.py',
)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = main_config.SECRET_KEY
DEBUG = main_config.DEBUG

ALLOWED_HOSTS = ['*']
ROOT_URLCONF = 'todo.urls'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'users.backend.UserEmailAuthentication',
]

ACCOUNT_AUTHENTICATION_METHOD = 'email'
AUTH_USER_MODEL = 'users.User'
WSGI_APPLICATION = 'todo.wsgi.application'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r'^/api/.*$'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_filters',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',
    'django_celery_beat',
    'diary',
    'users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': REDIS_URL+'/0',
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1']

