"""
WSGI config for ge_test project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

import sys
sys.path.append('C:/Users/Administrator/Desktop/django網站整合tiptop/ge_test')
'''
paths = [
    'C:/Users/Administrator/Desktop/django網站整合tiptop/ge_test',
    'C:/Users/Administrator/AppData/Local/Programs/Python/Python36-32/Lib/site-packages/',
]
for path in paths:
    if path not in sys.path:
        sys.path.append(path)
'''
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ge_test.settings')

application = get_wsgi_application()
