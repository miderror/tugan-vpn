from pathlib import Path

import environ

env = environ.Env()

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS")

INSTALLED_APPS = [
    "config.admin.CustomAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = []

ADMIN_MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": "postgres",
        "PORT": env("POSTGRES_PORT"),
        "CONN_MAX_AGE": 300,
        "OPTIONS": {
            "connect_timeout": 5,
            "pool": {
                "min_size": 1,
                "max_size": 4,
                "timeout": 10,
            },
        },
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static_root"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN")
YOOKASSA_SHOP_ID = env("YOOKASSA_SHOP_ID")
YOOKASSA_SECRET_KEY = env("YOOKASSA_SECRET_KEY")

REDIS_HOST = env("REDIS_HOST")
REDIS_PORT = env("REDIS_PORT")
REDIS_DB_FSM = env("REDIS_DB_FSM")

ADMIN_SITE_HEADER = "Tugan VPN Admin"
ADMIN_SITE_TITLE = "Панель управления"
ADMIN_INDEX_TITLE = "Добро пожаловать"
ADMIN_REORDER = [
    {"label": "👥 Пользователи", "models": ["users"]},
    {"label": "🛡️ VPN и Подписки", "models": ["access"]},
    {"label": "💰 Платежи", "models": ["billing"]},
    {"label": "🔔 Уведомления", "models": ["notifications"]},
    {"label": "⏱️ Планировщик", "models": ["django_celery_beat"]},
]
