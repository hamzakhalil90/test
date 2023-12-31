"""
Django settings for LCLPD_backend project.

Generated by 'django-admin startproject' using Django 4.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
# Data from the environment file
if not os.environ.get("DEBUG"):
    print("Please specify DEBUG variable in .env file")
debug = False if os.environ.get("DEBUG").lower() == "false" else True

if not os.environ.get("DATABASE_NAME"):
    print("Please specify DATABASE_NAME variable in .env file")
DATABASE_NAME = os.environ.get("DATABASE_NAME")

if not os.environ.get("DATABASE_USERNAME"):
    print("Please specify DATABASE_PASSWORD variable in .env file")
DATABASE_USERNAME = os.environ.get("DATABASE_USERNAME")

if not os.environ.get("DATABASE_PASSWORD"):
    print("Please specify DATABASE_PASSWORD variable in .env file")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")

if not os.environ.get("DATABASE_HOST"):
    print("Please specify 'DATABASE_HOST' variable in .env file")
DATABASE_HOST = os.environ.get("DATABASE_HOST")

if not os.environ.get("DATABASE_PORT"):
    print("Please specify 'DATABASE_PORT' variable in .env file")
DATABASE_PORT = os.environ.get("DATABASE_PORT")

if not os.environ.get("JWT_ENCODING_ALGO"):
    print("Please specify JWT_ENCODING_ALGO' variable in .env file")
JWT_ENCODING_ALGO = os.environ.get("JWT_ENCODING_ALGO")

if not os.environ.get("JWT_ENCODING_SECRET_KEY"):
    print("Please specify 'JWT_ENCODING_SECRET_KEY' variable in .env file")
JWT_ENCODING_SECRET_KEY = os.environ.get("JWT_ENCODING_SECRET_KEY")

if not os.environ.get("ENVIRONMENT"):
    print("Please specify 'ENVIRONMENT' variable in .env file")
ENVIRONMENT = os.environ.get("ENVIRONMENT")

if not os.environ.get("JWT_TOKEN_EXPIRY_DELTA"):
    print("Please specify 'JWT_TOKEN_EXPIRY_DELTA' variable in .env file")
JWT_TOKEN_EXPIRY_DELTA = os.environ.get("JWT_TOKEN_EXPIRY_DELTA")

if not os.environ.get("AWS_S3_ACCESS_KEY_ID"):
    print("Please specify AWS_S3_ACCESS_KEY_ID' variable in .env file")
if not os.environ.get("AWS_S3_SECRET_ACCESS_KEY"):
    print("Please specify AWS_S3_SECRET_ACCESS_KEY' variable in .env file")
if not os.environ.get("AWS_STORAGE_BUCKET_NAME"):
    print("Please specify AWS_STORAGE_BUCKET_NAME' variable in .env file")
if not os.environ.get("AWS_S3_REGION_NAME"):
    print("Please specify AWS_S3_REGION_NAME variable in .env file")

if not os.environ.get("ALLOWED_HOSTS"):
    print("Please specify ALLOWED_HOSTS variable in .env file")
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*")

# if not os.environ.get("CORS_ALLOWED_ORIGINS"):
#     print("Please specify CORS_ALLOWED_ORIGINS variable in .env file")
# CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS")
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-8bs7$&o=5dw37j-duwwnso&*i#zncd=k6117m789gsx0appkoe"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = debug

ALLOWED_HOSTS = [ALLOWED_HOSTS]
# if not CORS_ALLOWED_ORIGINS:
#     ...
# else:
#     CORS_ALLOWED_ORIGINS = [CORS_ALLOWED_ORIGINS]
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_HEADERS = ["*"]
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # project apps
    'user_management',
    'area_management',
    'channel_management',
    'inventory_management',
    'notifications_management',
    'system_logs',
    'workflows',

    # third party packages
    "drf_yasg",
    "corsheaders",
    "rest_framework",
    "market_intelligence",
    "django_crontab",
    'django_mysql',
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "user_management.custom_middleware.LockoutMiddleware",
]

ROOT_URLCONF = "LCLPD_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "LCLPD_backend.wsgi.application"

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
}

# Database configurations
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": DATABASE_NAME,
        "USER": DATABASE_USERNAME,
        "PASSWORD": DATABASE_PASSWORD,
        "HOST": DATABASE_HOST,
        "PORT": DATABASE_PORT,
    },
    "test": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

# "ENGINE": "django.db.backends.postgresql_psycopg2",
#         "NAME": os.getenv("POSTGRES_DB", DATABASE_NAME),
#         "USER": os.getenv("POSTGRES_USER", DATABASE_USERNAME),
#         "PASSWORD": os.getenv("POSTGRES_PASSWORD", DATABASE_PASSWORD),
#         "HOST": os.getenv("DB_HOST", DATABASE_HOST),
#         "PORT": os.getenv("DB_PORT", DATABASE_PORT),

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Basic": {"type": "basic"},
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"},
    }
}
# cronjob configurations
# 30 3 * * 1-6 (for every monday to saturday at 8:30am)
# CRONJOBS = [("30 3 * * 1-6", "user_management.cron.superuser_password_alert",
#              ">> " + os.path.join(BASE_DIR, "cronjob_logs/new_password_to_SA_logs.log"),)]

# Email configurations

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.office365.com"
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = "sales.notifications@lucky-cement.com"
EMAIL_HOST_PASSWORD = "Unlucky@1234"
#
# EMAIL_HOST_USER = "no-reply@joyn.com.pk"
# EMAIL_HOST_PASSWORD = "@Reply123"


# default user authentication model
AUTH_USER_MODEL = "user_management.User"

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# custom authentication backend configurations
AUTHENTICATION_BACKENDS = ["utils.base_authentication.AuthenticationBackend"]

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media/")

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_S3_ACCESS_KEY_ID = os.environ.get("AWS_S3_ACCESS_KEY_ID")
AWS_S3_SECRET_ACCESS_KEY = os.environ.get("AWS_S3_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME")
AWS_S3_CUSTOM_DOMAIN = os.environ.get("AWS_S3_CUSTOM_DOMAIN")
