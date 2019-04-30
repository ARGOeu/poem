from django.contrib.admin.sites import AdminSite
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.cache import never_cache

from Poem.poem_super_admin.admin_interface.siteprobes import ProbeAdmin
from Poem.poem_super_admin.admin_interface.sitetenant import TenantAdmin
from Poem.poem_super_admin.admin_interface.userprofile import \
    SuperUserProfileAdmin
from Poem.poem_super_admin.models import Probe
from Poem.tenants.models import Tenant
from Poem.users.models import CustUser


class SuperAdminSite(AdminSite):
    @never_cache
    def index(self, request, extra_context=None):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return HttpResponseRedirect(request.path + 'tenants')

    def app_index(self, request, app_label, extra_context=None):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                app_list = self.get_app_list(request)

                order = ['poem_super_admin', 'tenants', 'users']
                app_list = sorted(
                    app_list, key=lambda a: order.index(a['app_label'])
                )

                extra_context = dict(
                    self.each_context(request),
                    app_list=app_list
                )
                extra_context.update(extra_context or {})

                request.current_app = self.name

                return super().app_index(request, app_label, extra_context)

    @never_cache
    def logout(self, request, extra_context=None):
        super().logout(request, extra_context=extra_context)
        return HttpResponseRedirect(reverse('superadmin:index'))


mysuperadmin = SuperAdminSite(name='superadmin')
mysuperadmin.register(Tenant, TenantAdmin)
mysuperadmin.register(CustUser, SuperUserProfileAdmin)
mysuperadmin.register(Probe, ProbeAdmin)
