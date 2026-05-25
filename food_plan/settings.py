from pathlib import Path

import environ
from django.core.exceptions import ImproperlyConfigured

env = environ.Env()

BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
USE_MINIO = env.bool("USE_MINIO", default=True)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core.apps.CoreConfig",
]

if USE_MINIO:
    MINIO_ENDPOINT = env("MINIO_ENDPOINT")
    MINIO_ACCESS_KEY = env("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = env("MINIO_SECRET_KEY")
    MINIO_BUCKET_NAME = env("MINIO_BUCKET_NAME")
    MINIO_USE_SSL = env.bool("MINIO_USE_SSL", default=True)
    if not all([MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET_NAME]):
        raise ImproperlyConfigured(
            "MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, and MINIO_BUCKET_NAME "
            "are required when USE_MINIO=True."
        )

    INSTALLED_APPS.append("storages")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "food_plan.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "core" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "food_plan.wsgi.application"

DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "core.password_validators.CustomUserAttributeSimilarityValidator",
    },
    {
        "NAME": "core.password_validators.CustomMinimumLengthValidator",
    },
    {
        "NAME": "core.password_validators.CustomCommonPasswordValidator",
    },
    {
        "NAME": "core.password_validators.CustomNumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "core" / "static",
]

if USE_MINIO:
    STORAGES = {
        "default": {"BACKEND": "food_plan.storage.MediaStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
    MEDIA_URL = f"{'https' if MINIO_USE_SSL else 'http'}://{MINIO_ENDPOINT}/{MINIO_BUCKET_NAME}/media/"
    AWS_S3_ENDPOINT_URL = f"{'https' if MINIO_USE_SSL else 'http'}://{MINIO_ENDPOINT}"
    AWS_ACCESS_KEY_ID = MINIO_ACCESS_KEY
    AWS_SECRET_ACCESS_KEY = MINIO_SECRET_KEY
    AWS_STORAGE_BUCKET_NAME = MINIO_BUCKET_NAME
    AWS_S3_REGION_NAME = ""
    AWS_S3_CUSTOM_DOMAIN = f"{MINIO_ENDPOINT}/{MINIO_BUCKET_NAME}"
    AWS_QUERYSTRING_EXPIRE = 3600
else:
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")

YOOKASSA_SHOP_ID = env("YOOKASSA_SHOP_ID", default="") if DEBUG else env("YOOKASSA_SHOP_ID")
YOOKASSA_SECRET_KEY = env("YOOKASSA_SECRET_KEY", default="") if DEBUG else env("YOOKASSA_SECRET_KEY")

LOG_DIR = Path(env("LOG_DIR", default=str(BASE_DIR / "logs")))
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} {levelname} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "app.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "core": {
            "handlers": ["console", "file"],
            "level": "INFO" if DEBUG else "WARNING",
        },
    },
}
