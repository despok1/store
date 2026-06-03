from .base import *
from dotenv import load_dotenv
import os

load_dotenv()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Hosts allowed to serve the app
ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS').split(",") if host.strip()]

# NGROK: if you expose the local server with ngrok, set NGROK_URL in .env
NGROK_URL = os.getenv('NGROK_URL')
if NGROK_URL:
    CSRF_TRUSTED_ORIGINS = [NGROK_URL]
else:
    CSRF_TRUSTED_ORIGINS = ['http://localhost', 'http://127.0.0.1']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('PGDATABASE', 'store'),
        'USER': os.getenv('PGUSER', 'postgres'),
        'PASSWORD': os.getenv('PGPASSWORD', 'password'),
        'HOST': os.getenv('PGHOST', 'localhost'),
        'PORT': os.getenv('PGPORT', '5432'),
    }
}

# Email settings (console backend for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# Development server port
PORT = os.getenv('PORT', '8000')