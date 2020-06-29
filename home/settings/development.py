from .settings import INSTALLED_APPS, MIDDLEWARE

ALLOWED_HOSTS = '*'
INSTALLED_APPS.append('corsheaders')
MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware'] + MIDDLEWARE
CORS_ORIGIN_ALLOW_ALL = True
