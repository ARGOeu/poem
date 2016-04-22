import os

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.http import HttpResponseRedirect
from django.core import urlresolvers
from django_logging import django_logging
from django.conf.urls.static import static

from ajax_select import urls as ajax_select_urls
from Poem.settings import URL_DEBUG
from Poem.poem.admin import myadmin

django_logging()

urlpatterns = patterns('',
                       (r'^$', lambda x: HttpResponseRedirect('/poem/admin')),
                       (r'^admin/lookups/', include(ajax_select_urls)),
                       (r'^admin/', include(myadmin.urls)),
                       (r'^api/', include('Poem.urls_api')),
)

# import ipdb; ipdb.set_trace()  # XXX BREAKPOINT

if URL_DEBUG:
    urlpatterns = patterns('', url(r'^poem/', include(urlpatterns)),) + static('/poem_media/', document_root='/usr/share/poem/media/')
