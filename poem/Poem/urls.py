import os

from django.conf.urls.defaults import patterns, include
from django.contrib import admin
from django.conf import settings
from django.http import HttpResponseRedirect
from django.core import urlresolvers
from django_logging import django_logging

from ajax_select import urls as ajax_select_urls

django_logging()

admin.autodiscover()

urlpatterns = patterns('',
                       (r'^$', lambda x: HttpResponseRedirect('/poem/admin/poem/profile')),
                       (r'^admin/lookups/', include(ajax_select_urls)),
                       (r'^admin/', include(admin.site.urls)),
                       (r'^api/', include('Poem.urls_api')),
)
