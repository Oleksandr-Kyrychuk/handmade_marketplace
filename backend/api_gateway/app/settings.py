import environ
import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
if os.getenv('ENV') == 'local':
    print("Loading .env.local")
    environ.Env.read_env(os.path.join(BASE_DIR, '.env.local'))
else:
    print("Loading .env")
    environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost").split(",")  # Додано для Render
# ALLOWED_HOSTS = ['*']
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'drf_spectacular',
    'app',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'app.urls'  # Змінено на app.urls, бо це API Gateway

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

WSGI_APPLICATION = 'app.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(default=env('DATABASE_URL'))
}
DATABASES['default']['OPTIONS'] = {'options': '-c search_path=gateway_schema,public'}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000000/day',
        'user': '10000000/day',
    },
}


CORS_ALLOWED_ORIGINS = env('CORS_ALLOWED_ORIGINS', default='http://localhost:5173,http://localhost:3000').split(',')
CORS_ALLOW_CREDENTIALS = True

REDIS_URL = env('REDIS_URL', default='redis://redis:6379/1')
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,
        },
        "TIMEOUT": 60 * 60,
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s %(name)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        # 'file': {
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     'filename': os.path.join(BASE_DIR, 'logs', 'api_gateway.log'),
        #     'maxBytes': 10 * 1024 * 1024,
        #     'backupCount': 5,
        #     'formatter': 'verbose',
        # },
    },
    'loggers': {
    'django': {
        'handlers': ['console'],  # прибрали 'file'
        'level': 'INFO',
        'propagate': False,
    },
    'app': {
        'handlers': ['console'],  # прибрали 'file'
        'level': 'DEBUG',
        'propagate': False,
    },
}
}

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

SPECTACULAR_SETTINGS = {
    'TITLE': 'Handmade Marketplace API Gateway',
    'DESCRIPTION': 'API Gateway for Handmade Marketplace',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}