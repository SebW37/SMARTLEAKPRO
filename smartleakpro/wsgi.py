"""
WSGI config for SmartLeakPro project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartleakpro.settings_simple')

application = get_wsgi_application()
