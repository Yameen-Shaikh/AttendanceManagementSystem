from .base import *

# TEMPORARY - Hardcoded secret key for debugging
SECRET_KEY = 'temporary-secret-key-for-debugging-purposes-please-change'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Add your PythonAnywhere domain and any other domains you use.
ALLOWED_HOSTS = [
    'Yameen.pythonanywhere.com',
]

# It's recommended to set this for HTTPS connections.
CSRF_TRUSTED_ORIGINS = [
    'https://Yameen.pythonanywhere.com',
]

# STATIC_ROOT is the directory where Django will collect all static files.
# PythonAnywhere will then serve files from this directory.
STATIC_ROOT = BASE_DIR / 'staticfiles'

# You should also configure your production database here.
# For example, using MySQL on PythonAnywhere:
#
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'Yameen$default',
        'USER': 'Yameen',
        'PASSWORD': 'ams_server',
        'HOST': 'Yameen.mysql.pythonanywhere-services.com',
    }
}
