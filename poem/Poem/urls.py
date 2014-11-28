import os

from django.conf.urls.defaults import patterns, include
from django.contrib import admin
from django.conf import settings
from django.http import HttpResponseRedirect
from django.core import urlresolvers

from django_logging import django_logging

django_logging()

admin.autodiscover()

urlpatterns = patterns('',
                       (r'^$', lambda x: HttpResponseRedirect('/poem/admin/poem/profile')),
#                       (r'^$', lambda x: HttpResponseRedirect(urlresolvers.reverse('admin:poem_profile_changelist'))),
                       (r'^api/', include('Poem.poem_api.urls')),
                       (r'^admin/', include(admin.site.urls)),
                       (r'^poem_media/(.*)$', 'django.views.static.serve',
                                    {'document_root': os.path.join(settings.APP_PATH, '../media')}),
)
