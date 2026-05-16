from .base import *
import os


MIDDLEWARE += [
    'whitenoise.middleware.WhiteNoiseMiddleware',
]
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError('SECRET_KEY environment variable is not set')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False





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
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

