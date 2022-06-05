""" Production settings
"""
import os

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = False
ALLOWED_HOSTS = ["*"]

# CSRF
# https://docs.djangoproject.com/en/4.0/ref/settings/#csrf-trusted-origins
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS").split(";")

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

# Security
# https://docs.djangoproject.com/en/3.0/topics/security/

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = "same-origin"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True

# Email
# https://docs.djangoproject.com/zh-hans/3.0/topics/email/

EMAIL_HOST = "smtp.exmail.qq.com"
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
SERVER_EMAIL = os.getenv("EMAIL_HOST_USER")
DEFAULT_FROM_EMAIL = os.getenv("EMAIL_HOST_USER")
ADMINS = [
    admin
    for admin in zip(
        os.getenv("ADMINS_NAME").split(";"),
        os.getenv("ADMINS_EMAIL").split(";"),
    )
]

# Celery
# https://docs.celeryproject.org/en/stable/getting-started/brokers/redis.html

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

# EMQX HTTP
# https://docs.emqx.io/broker/latest/cn/advanced/http-api.html

EMQX_HTTP_HOST = os.getenv("EMQX_HTTP_HOST")
EMQX_HTTP_PORT = os.getenv("EMQX_HTTP_PORT")
EMQX_HTTP_APPID = os.getenv("EMQX_HTTP_APPID")
EMQX_HTTP_APPSECRET = os.getenv("EMQX_HTTP_APPSECRET")

# 小米小爱
# https://developers.xiaoai.mi.com/documents/Home?type=/api/doc/render_markdown/SkillAccess/SkillDocument/CustomSkills/Signature

XIAOAI_KEY_ID = os.getenv("XIAOAI_KEY_ID")
XIAOAI_SECRET = os.getenv("XIAOAI_SECRET")

# 小米推送
# https://dev.mi.com/console/doc/detail?pId=1788

MI_PUSH_PACKAGE_NAME = os.getenv("MI_PUSH_PACKAGE_NAME")
MI_PUSH_APP_ID = os.getenv("MI_PUSH_APP_ID")
MI_PUSH_APP_KEY = os.getenv("MI_PUSH_APP_KEY")
MI_PUSH_APP_SECRET = os.getenv("MI_PUSH_APP_SECRET")

# https://docs.djangoproject.com/zh-hans/3.1/ref/settings/#media-url

MEDIA_URL = os.getenv("MEDIA_URL")

# Django Storages(S3)
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html

if os.getenv("AWS_S3_ENDPOINT_URL"):
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

    MEDIA_ROOT = ""

    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")

    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")
