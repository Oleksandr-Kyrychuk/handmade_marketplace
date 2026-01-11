import environ
import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# 1. Ініціалізація env з defaults (додаємо більше типів і значень за замовчуванням)
env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, 'django-insecure-change-me-in-production!'),
    DATABASE_URL=(str, 'postgresql://dev:dev@localhost:5432/marketplace'),
    USER_SERVICE_URL=(str, 'http://user-service:8001'),
    CLOUD_NAME=(str, ''),
    API_KEY=(str, ''),
    API_SECRET=(str, ''),
    REDIS_URL=(str, 'redis://redis:6379/1'),
    CORS_ALLOWED_ORIGINS=(str, 'http://localhost:5173,http://localhost:3000'),
    # Додаємо для продакшену
    ALLOWED_HOSTS=(str, 'localhost,127.0.0.1'),
    STATIC_URL=(str, '/static/'),
    MEDIA_URL=(str, '/media/'),
)

# 2. Завантаження .env (залишаємо як є)
env_path = BASE_DIR / ('.env.local' if os.getenv('ENV') == 'local' else '.env')
if env_path.exists():
    print(f"Loading {env_path.name}")
    environ.Env.read_env(str(env_path))
else:
    print(f"{env_path.name} not found — using Docker environment variables")

# 3. Cloudinary (додаємо перевірку на порожні значення)
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUD_NAME'),
    'API_KEY': env('API_KEY'),
    'API_SECRET': env('API_SECRET'),
}

# Основні налаштування
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')

# Додаємо для прод: завжди використовувати ALLOWED_HOSTS з env
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

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
    'products',
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

ROOT_URLCONF = 'product_service.urls'

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

WSGI_APPLICATION = 'product_service.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(default=env('DATABASE_URL'))
}
DATABASES['default']['OPTIONS'] = {'options': '-c search_path=products_schema,public'}

# REST Framework (додаємо пагинацію за замовчуванням)
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
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,  # додай, якщо хочеш обмежити кількість елементів
}

CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=['http://localhost:5173', 'http://localhost:3000'])
CORS_ALLOW_CREDENTIALS = True

# Celery (додаємо retry для прод)
REDIS_URL = env('REDIS_URL', default='redis://redis:6379/1')
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default=REDIS_URL)
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default=REDIS_URL)
CELERY_TASK_DEFAULT_QUEUE = 'product_queue'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True  # додай для стабільності

# Static & Media (критично для прод)
STATIC_URL = env('STATIC_URL', default='/static/')
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = env('MEDIA_URL', default='/media/')
MEDIA_ROOT = BASE_DIR / 'media'

# Whitenoise для прод (додай в requirements.txt: whitenoise)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Логування (додаємо файл для прод)
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
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs/product.log',
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'products': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Product Service API',
    'DESCRIPTION': 'Products, reviews, moderation, images',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,  # в проді краще False, щоб не віддавати /schema
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': r'^/?.*',
    'OPERATION_ID_SUFFIX': 'ViewSet',
    'TAGS': [
        {'name': 'products', 'description': 'Products CRUD & filtering'},
        {'name': 'reviews', 'description': 'Product reviews'},
        {'name': 'moderation', 'description': 'Content moderation'},
    ],
    'GENERATE_UNIQUE_ID_FUNCTION': lambda view: f"{view.__class__.__name__}_{view.action or 'index'}",
'POSTPROCESSING_HOOKS': [
        'drf_spectacular.hooks.postprocess_schema_enums',
        'products.hooks.postprocess_unified_schema',
    ],
}

# Додай для безпеки в проді
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
