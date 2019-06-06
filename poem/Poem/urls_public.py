from django.conf.urls import include
from django.http import HttpResponseRedirect
from django.urls import re_path

from Poem.poem_super_admin.admin import mysuperadmin

urlpatterns = [
    re_path(r'^$', lambda x: HttpResponseRedirect('/poem/superadmin/')),
    re_path(r'^superadmin/', mysuperadmin.urls),
    re_path(r'^saml2/', include(('djangosaml2.urls', 'poem'),
                                namespace='saml2')),
]
