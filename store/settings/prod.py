from .base import *
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

INSTALLED_APPS += [
    "storages",
]

# WhiteNoise should be inserted right after SecurityMiddleware.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
] + MIDDLEWARE[1:]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError('SECRET_KEY environment variable is not set')

# MEDIA_URL = '/media/'




AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL')

AWS_S3_CUSTOM_DOMAIN = os.environ.get('AWS_S3_CUSTOM_DOMAIN', '')

AWS_QUERYSTRING_AUTH = False
# AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'auto')
# AWS_S3_SIGNATURE_VERSION = 's3v4'
# AWS_DEFAULT_ACL = None
# AWS_S3_OBJECT_PARAMETERS = {
#     'CacheControl': 'max-age=86400',
# }


# CSRF trusted origins for Railway
raw_csrf_trusted_origins = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
CSRF_TRUSTED_ORIGINS = []
if raw_csrf_trusted_origins:
    for origin in raw_csrf_trusted_origins.split(','):
        origin = origin.strip()
        if not origin:
            continue
        if origin.startswith(('http://', 'https://')):
            CSRF_TRUSTED_ORIGINS.append(origin)
        else:
            CSRF_TRUSTED_ORIGINS.append(f'https://{origin}')

# Email settings for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


# Security settings for production

# Disabled to prevent redirect loops when Railway proxies the request.
# Railway's edge handles TLS termination; the app itself should not redirect.
SECURE_SSL_REDIRECT = False

# Trust Railway's proxy to forward the correct host header.
USE_X_FORWARDED_HOST = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'


# Set MEDIA_URL for R2
# if AWS_S3_CUSTOM_DOMAIN:
#     MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
# elif AWS_STORAGE_BUCKET_NAME:
#     MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.r2.dev/'
# else:

STORAGES = {
    "default": {
        # "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "location": "",
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        "OPTIONS": {},
    },
}

