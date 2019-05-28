from django.conf.urls import include, url
from django.db import connection
from django.http import HttpResponseRedirect
from tenant_schemas.utils import get_public_schema_name
from Poem.django_logging import django_logging

from ajax_select import urls as ajax_select_urls
from Poem.poem.admin import myadmin
from Poem.poem_super_admin.admin import mysuperadmin

django_logging()

if connection.get_tenant().schema_name == get_public_schema_name():
    ad = 'superadmin/'
else:
    ad = 'admin/'

# Apache settings
urlpatterns = [
    url(r'^$', lambda x: HttpResponseRedirect('/poem/' + ad)),
    url(r'^admin/', myadmin.urls),
    url(r'^superadmin/', mysuperadmin.urls),
    url(r'^admin/lookups/', include(ajax_select_urls)),
    url(r'^api/0.2/', include('Poem.poem.urls')),
    url(r'^api/v2/', include('Poem.api.urls', namespace='poemapi')),
    url(r'^saml2/', include(('djangosaml2.urls', 'poem'), namespace='saml2')),
]

# Django development server settings
# urlpatterns = [
#     url(r'^$', lambda x: HttpResponseRedirect('/poem/admin/')),
#     url(r'^admin/', myadmin.urls),
#     url(r'^admin/lookups/', include(ajax_select_urls)),
#     url(r'^api/', include('Poem.urls_api')),
#     url(r'^saml2/', include(('djangosaml2.urls', 'poem'), namespace='saml2')),
# ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
#     static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
