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
import re


class PublicViews(object):
    def load_settings(self):
        self.public_models = (Probe,)
        self._map = dict()
        _ = [self._map.update({x.__name__.lower(): x}) for x in
             self.public_models]
        self._regex = '(' + '|'.join([s.__name__.lower()
                                      for s in self.public_models]) + ')'

    def get_public_urls(self):
        from django.urls import re_path

        public_urls = list()
        public_urls.append(
            re_path(
                '^poem_super_admin/public_(?P<model>%s)/$' % self._regex,
                self.public_views
            )
        )
        public_urls.append(
            re_path(
                '^poem_super_admin/public_(?P<model>%s)/(?P<object_id>[0-9]+)/change/'
                % self._regex, self.public_views
            )
        )
        public_urls.append(
            re_path(
                '^poem_super_admin/public_(?P<model>%s)/(?P<object_id>[0-9]+)/history/(?P<rev_id>[0-9]+)/'
                % self._regex, self.public_views
            )
        )

        return public_urls

    def public_views(self, request, **kwargs):
        objid = kwargs.get('object_id', None)
        revid = kwargs.get('rev_id', None)
        model = self._map[kwargs['model']]
        context = dict(self.each_context(request))
        if objid and not revid:
            return self._registry[model].change_view(request, objid,
                                                     extra_context=context)
        elif objid and revid:
            return self._registry[model].revision_view(request, objid, revid,
                                                       extra_context=context)
        else:
            return self._registry[model].changelist_view(request,
                                                         extra_context=context)

    def login(self, request, extra_context):
        prev = request.META.get('HTTP_REFERER', None)
        if prev:
            context = dict(self.each_context(request))
            next_url = request.GET.get('next')
            rn = re.search(
                'poem_super_admin/(?P<model>%s)/' % self._regex, next_url
            )

            r = re.search('public_(\w+)/', prev)
            if r:
                objid = re.search('([0-9]+)/change/', next_url)
                if objid:
                    # changelist_view -> change_view
                    objid = objid.group(1)
                    url = reverse(
                        'admin:poem_super_admin_%s_change' % rn.group('model'),
                        args=(objid,)
                    )
                    url = url.replace(rn.group('model') + '/',
                                      'public_%s/' % rn.group('model'))

                    return HttpResponseRedirect(url)
                else:
                    # changelist_view -> changelist_view
                    url = reverse(
                        'admin:poem_super_admin_%s_changelist'
                        % rn.group('model')
                    )
                    url = url.replace(rn.group('model') + '/',
                                      'public_%s/' % rn.group('model'))

                    return HttpResponseRedirect(url)

            # change_view -> changelist_view
            r = re.search('public_(\w+)/([0-9]+)/change/$', prev)
            if r:
                url = reverse(
                    'admin:poem_super_admin_%s_changelist' % rn.group('model')
                )
                url = url.replace(rn.group('model') + '/',
                                  'public_%s/' % rn.group('model'))

                return HttpResponseRedirect(url)


        return super().login(request, extra_context)


class SuperAdminSite(PublicViews, AdminSite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        super().load_settings()

    @never_cache
    def index(self, request, extra_context=None):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return HttpResponseRedirect(request.path + 'poem_super_admin')

    @never_cache
    def login(self, request, extra_context=None):
        extra_context = extra_context if extra_context else dict()

        return super().login(request, extra_context)

    def app_index(self, request, app_label, extra_context=None):
        if request.user.is_authenticated:
            if request.user.is_superuser:

                if request.path.endswith('superadmin/tenants/'):
                    return HttpResponseRedirect(
                        '/poem/superadmin/poem_super_admin/'
                    )

                if request.path.endswith('superadmin/users/'):
                    return HttpResponseRedirect(
                        '/poem/superadmin/poem_super_admin/'
                    )

                app_list = self.get_app_list(request)

                for a in app_list:
                    if a['app_label'] == 'poem_super_admin':
                        a['name'] = 'Shared data'

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

    def get_urls(self):
        return super().get_urls() + super().get_public_urls()

    @never_cache
    def logout(self, request, extra_context=None):
        super().logout(request, extra_context=extra_context)
        return HttpResponseRedirect(reverse('superadmin:index'))


mysuperadmin = SuperAdminSite(name='superadmin')
mysuperadmin.register(Tenant, TenantAdmin)
mysuperadmin.register(CustUser, SuperUserProfileAdmin)
mysuperadmin.register(Probe, ProbeAdmin)
