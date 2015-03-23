import sys
import os
from distutils.sysconfig import get_python_lib

sys.path.append(get_python_lib() + '/django/contrib/admin/static/admin/')
sys.path.append('/usr/share/poem')
os.environ['DJANGO_SETTINGS_MODULE'] = 'Poem.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
