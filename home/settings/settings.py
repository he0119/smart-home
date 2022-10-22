"""
Django settings for home project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.redis import RedisIntegration

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.getcwd()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "nu$#aq5e6x27t*j&hc4joq7y*wsvktqm-98oa=tqe6l+ch@hsq"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# LOGGING
# https://docs.djangoproject.com/zh-hans/3.0/topics/logging/

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "verbose": {
            "format": "{asctime} - {name} - {levelname} - {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S %Z",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "level": "INFO",
            "filters": ["require_debug_false"],
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "verbose",
            "filename": os.path.join(BASE_DIR, "logs", "smart-home.log"),
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 10,
            "encoding": "utf8",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "iot": {
            "handlers": ["console", "file", "mail_admins"],
            "level": "DEBUG",
        },
        "xiaoai": {
            "handlers": ["console", "file", "mail_admins"],
            "level": "DEBUG",
        },
    },
}

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 数据相关
    "mptt",
    "django_celery_beat",
    "django_cleanup",
    # GraphQL
    "channels",
    "strawberry.django",
    "strawberry_django_plus",
    # 我的应用
    "home.users",
    "home.storage",
    "home.board",
    "home.xiaoai",
    "home.iot",
    "home.push",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "home.users.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "home.urls"

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

# Channels
# https://channels.readthedocs.io/en/stable/topics/channel_layers.html

ASGI_APPLICATION = "home.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.pubsub.RedisPubSubChannelLayer",
        "CONFIG": {"hosts": ["redis://localhost:6379"]},
    },
}

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "zh-Hans"

TIME_ZONE = "Asia/Shanghai"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Login
# https://docs.djangoproject.com/zh-hans/4.0/topics/auth/default/

LOGIN_URL = "/admin/"

# MPTT
# https://django-mptt.readthedocs.io/en/latest/forms.html

MPTT_DEFAULT_LEVEL_INDICATOR = "--"

# Celery
# https://docs.celeryproject.org/en/stable/getting-started/brokers/redis.html

CELERY_BROKER_URL = "redis://localhost:6379"
CELERY_RESULT_BACKEND = "redis://localhost:6379"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

# Celery Beats
# https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html#beat-custom-schedulers

CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# 小米小爱
# https://developers.xiaoai.mi.com/documents/Home?type=/api/doc/render_markdown/SkillAccess/SkillDocument/CustomSkills/Signature

XIAOAI_KEY_ID = "key_id"
XIAOAI_SECRET = "c2VjcmV0"

# 小米推送
# https://dev.mi.com/console/doc/detail?pId=1788

MI_PUSH_PACKAGE_NAME = "package_name"
MI_PUSH_APP_ID = "app_id"
MI_PUSH_APP_KEY = "app_key"
MI_PUSH_APP_SECRET = "app_secret"

# Files
# https://docs.djangoproject.com/zh-hans/3.1/topics/files/

MEDIA_ROOT = "media"

# AutoField
# https://docs.djangoproject.com/en/3.2/releases/3.2/#customizing-type-of-auto-created-primary-keys

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Sentry
# https://docs.sentry.io/platforms/python/guides/django/
# https://docs.sentry.io/platforms/python/guides/django/performance/#configure-the-sample-rate

sentry_sdk.init(
    integrations=[DjangoIntegration(), RedisIntegration(), HttpxIntegration()],
    send_default_pii=True,
    # 性能监控的比例
    # 必须设置才会启用性能监控
    # Set traces_sample_rate to 1.0 to capture 100%
    traces_sample_rate=1.0,
    # 会在 Actions 自动编译的过程中修改
    release="version",
)

# 自定义会话
# https://docs.djangoproject.com/en/4.0/ref/contrib/gis/geoip2/

SESSION_ENGINE = "home.users.models"
SESSION_SAVE_EVERY_REQUEST = True

# GeoIP2
# https://dev.maxmind.com/geoip/geolite2-free-geolocation-data?lang=en

GEOIP_PATH = os.path.join(BASE_DIR, "geoip")
