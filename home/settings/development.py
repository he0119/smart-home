""" 开发环境配置
"""
import os

from .settings import INSTALLED_APPS, MIDDLEWARE

ALLOWED_HOSTS = '*'
INSTALLED_APPS.append('corsheaders')
MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware'] + MIDDLEWARE
CORS_ORIGIN_ALLOW_ALL = True

# 开发服务器配置，从环境变量里读取
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': os.getenv('POSTGRES_PORT'),
    }
}
