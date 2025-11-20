import environ
import os
from pathlib import Path
import dj_database_url
from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, 'django-insecure-change-me-in-production!'),
    DATABASE_URL=(str, 'postgresql://dev:sysadmin@localhost:5432/marketplace'),  # Default як в product, але з sysadmin
    USER_SERVICE_URL=(str, 'http://user-service:8001'),
    PRODUCT_SERVICE_URL=(str, 'http://product-service:8002'),
    ORDER_SERVICE_URL=(str, 'http://order-service:8003'),
    REDIS_URL=(str, 'redis://redis:6379/1'),
    CORS_ALLOWED_ORIGINS=(str, 'http://localhost:5173,http://localhost:3000'),
)

env_path = BASE_DIR / ('.env.local' if os.getenv('ENV') == 'local' else '.env')
if env_path.exists():
    print(f"Loading {env_path.name}")
    environ.Env.read_env(str(env_path))
else:
    print(f"{env_path.name} not found — using Docker environment variables")

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost").split(",")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'drf_spectacular',
    'django_celery_beat',
    'orders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'order_service.urls'

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

WSGI_APPLICATION = 'order_service.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(default=env('DATABASE_URL'))
}
DATABASES['default']['OPTIONS'] = {'options': '-c search_path=orders_schema,public'}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
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
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://redis:6379/1')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://redis:6379/1')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s %(name)s %(message)s',
        },
    },
    'filters': {
        'sensitive_filter': {
            '()': 'orders.log_filters.SensitiveDataFilter',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': ['sensitive_filter'],
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'orders': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


USER_SERVICE_URL = env('USER_SERVICE_URL')
PRODUCT_SERVICE_URL = env('PRODUCT_SERVICE_URL')
ORDER_SERVICE_URL = env('ORDER_SERVICE_URL')

CELERY_BEAT_SCHEDULE = {
    'cancel-pending-orders': {
        'task': 'orders.tasks.cancel_pending_orders',
        'schedule': crontab(minute=0, hour=0),  # щодня
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

SPECTACULAR_SETTINGS = {
    'TITLE': 'Order Service API',
    'DESCRIPTION': 'Cart, orders, checkout',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': r'^/?.*',
    'TAGS': [
        {'name': 'cart', 'description': 'Shopping cart'},
        {'name': 'orders', 'description': 'Order management'},
    ],
    'OPERATION_ID_SUFFIX': 'ViewSet',
    'GENERATE_UNIQUE_ID_FUNCTION': lambda view: f"{view.__class__.__name__}_{view.action or 'index'}",
}