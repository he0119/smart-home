""" Production settings
"""
import os

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = False
ALLOWED_HOSTS = '*'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_NAME'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': os.getenv('POSTGRES_PORT'),
    }
}

# Security
# https://docs.djangoproject.com/en/3.0/topics/security/

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = 'same-origin'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True

# Email
# https://docs.djangoproject.com/zh-hans/3.0/topics/email/

EMAIL_HOST = 'smtp.exmail.qq.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
SERVER_EMAIL = os.getenv('EMAIL_HOST_USER')
DEFAULT_FROM_EMAIL = os.getenv('EMAIL_HOST_USER')
ADMINS = [
    admin for admin in zip(
        os.getenv('ADMINS_NAME').split(';'),
        os.getenv('ADMINS_EMAIL').split(';'),
    )
]

# 小米小爱
# https://developers.xiaoai.mi.com/documents/Home?type=/api/doc/render_markdown/SkillAccess/SkillDocument/CustomSkills/Signature

XIAOAI_KEY_ID = os.getenv('XIAOAI_KEY_ID')
XIAOAI_SECRET = os.getenv('XIAOAI_SECRET')

# Celery
# https://docs.celeryproject.org/en/stable/getting-started/brokers/redis.html

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')

# EMQX HTTP
# https://docs.emqx.io/broker/latest/cn/advanced/http-api.html

EMQX_HOST = os.getenv('EMQX_HOST')
EMQX_PORT = os.getenv('EMQX_PORT')
EMQX_APPID = os.getenv('EMQX_APPID')
EMQX_APPSECRET = os.getenv('EMQX_APPSECRET')
