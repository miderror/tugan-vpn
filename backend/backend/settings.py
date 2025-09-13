from pathlib import Path
import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config.DJANGO_SECRET

DEBUG = False

ALLOWED_HOSTS = ['portar.org', 'localhost', '127.0.0.1']
CSRF_TRUSTED_ORIGINS = ['https://portar.org']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'api',
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
    'api.telegram_middleware.TWAAuthorizationMiddleware',
]

ROOT_URLCONF = 'backend.urls'

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

WSGI_APPLICATION = 'backend.wsgi.application'

DATABASES = {
    "default": {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config.DATABASE_NAME,
        'USER': config.DATABASE_LOGIN,
        'PASSWORD': config.DATABASE_PASSWORD,
        'HOST': config.DATABASE_HOST,
        'PORT': config.DATABASE_PORT,
        'CONN_MAX_AGE': 60,
        'CONN_HEALTH_CHECKS': True,
    }
}

TELEGRAM_SECRET_KEY = config.TELEGRAM_SECRET_KEY
ADMIN_IDS = config.ADMIN_IDS

XUI_CLUSTERS = config.XUI_CLUSTERS
XUI_ADMIN_USERNAME = config.XUI_ADMIN_USERNAME
XUI_ADMIN_PASSWORD = config.XUI_ADMIN_PASSWORD

TOTAL_GB = config.TOTAL_GB
TRIAL_TIME = config.TRIAL_TIME

YOOKASSA_SHOP_ID = config.YOOKASSA_SHOP_ID
YOOKASSA_SECRET_KEY = config.YOOKASSA_SECRET_KEY
WEBAPP_URL = config.WEBAPP_URL

WEBHOOK_HOST = config.WEBHOOK_HOST
WEBHOOK_PATH = config.WEBHOOK_PATH
WEBHOOK_PORT = config.WEBAPP_PORT
WEBHOOK_URL = config.WEBHOOK_URL

SUB_PATH = config.SUB_PATH
PUBLIC_LINK = config.PUBLIC_LINK

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

# AUTH_USER_MODEL = 'api.User'
CORS_ALLOW_ALL_ORIGINS = True

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = '/var/www/tgwebapp/backend/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
