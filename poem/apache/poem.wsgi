import sys
import os

sys.path.append('/usr/lib/python2.6/site-packages/django/contrib/admin/static/admin/')
sys.path.append('/usr/share/poem')
os.environ['DJANGO_SETTINGS_MODULE'] = 'Poem.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
