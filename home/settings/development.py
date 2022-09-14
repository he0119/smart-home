""" 开发环境配置
"""
import os

from .settings import INSTALLED_APPS, MIDDLEWARE, SECRET_KEY

ALLOWED_HOSTS = ["*"]
INSTALLED_APPS.append("corsheaders")
MIDDLEWARE = ["corsheaders.middleware.CorsMiddleware"] + MIDDLEWARE
CORS_ORIGIN_ALLOW_ALL = True

# _Debug Toolbar
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html
# https://blb-ventures.github.io/strawberry-django-plus/debug-toolbar/
INSTALLED_APPS.append("debug_toolbar")
MIDDLEWARE = [
    "strawberry_django_plus.middlewares.debug_toolbar.DebugToolbarMiddleware"
] + MIDDLEWARE
INTERNAL_IPS = ["127.0.0.1"]

# 开发服务器配置，从环境变量里读取
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_PORT"),
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.getenv("CHANNEL_REDIS_URL")],
            "symmetric_encryption_keys": [SECRET_KEY],
        },
    },
}

if os.getenv("AWS_S3_ENDPOINT_URL"):
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

    MEDIA_URL = os.getenv("MEDIA_URL")
    MEDIA_ROOT = ""

    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")

    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")
