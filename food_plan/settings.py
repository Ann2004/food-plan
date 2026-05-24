from pathlib import Path

import environ

env = environ.Env(
    DEBUG=(bool, True),
    MINIO_USE_SSL=(bool, False),
    USE_MINIO=(bool, False),
)

BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
USE_MINIO = env("USE_MINIO")
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
    MEDIA_URL = f"{'https' if env('MINIO_USE_SSL') else 'http'}://{env('MINIO_ENDPOINT')}/{env('MINIO_BUCKET_NAME')}/media/"
    AWS_S3_ENDPOINT_URL = f"{'https' if env('MINIO_USE_SSL') else 'http'}://{env('MINIO_ENDPOINT')}"
    AWS_ACCESS_KEY_ID = env("MINIO_ACCESS_KEY")
    AWS_SECRET_ACCESS_KEY = env("MINIO_SECRET_KEY")
    AWS_STORAGE_BUCKET_NAME = env("MINIO_BUCKET_NAME")
    AWS_S3_REGION_NAME = ""
    AWS_S3_CUSTOM_DOMAIN = f"{env('MINIO_ENDPOINT')}/{env('MINIO_BUCKET_NAME')}"
    AWS_QUERYSTRING_EXPIRE = 3600
else:
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

YOOKASSA_SHOP_ID = env("YOOKASSA_SHOP_ID", default="")
YOOKASSA_SECRET_KEY = env("YOOKASSA_SECRET_KEY", default="")
