"""
WSGI config for ams project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from django.core.wsgi import get_wsgi_application

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ams.settings.development')

application = get_wsgi_application()
