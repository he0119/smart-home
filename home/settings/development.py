"""开发环境配置"""

import os
import sys

from .settings import INSTALLED_APPS, MIDDLEWARE

# Corsheaders
# https://github.com/adamchainz/django-cors-headers#setup

ALLOWED_HOSTS = ["*"]
INSTALLED_APPS.append("corsheaders")
MIDDLEWARE = ["corsheaders.middleware.CorsMiddleware", *MIDDLEWARE]
CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = ["https://*"]

# _Debug Toolbar
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html
# https://strawberry-graphql.github.io/strawberry-django/integrations/debug-toolbar/

# Enable the debug toolbar only when not running tests
# https://github.com/jazzband/django-debug-toolbar/issues/1920
ENABLE_DEBUG_TOOLBAR = "test" not in sys.argv
if ENABLE_DEBUG_TOOLBAR:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE = [
        "strawberry_django.middlewares.debug_toolbar.DebugToolbarMiddleware",
        *MIDDLEWARE,
    ]
INTERNAL_IPS = ["127.0.0.1"]

if os.getenv("AWS_S3_ENDPOINT_URL"):
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

    MEDIA_URL = os.getenv("MEDIA_URL")
    MEDIA_ROOT = ""

    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")

    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")
