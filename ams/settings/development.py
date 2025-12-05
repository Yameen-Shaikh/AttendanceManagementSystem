from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '192.168.0.104', '192.168.0.102'] 