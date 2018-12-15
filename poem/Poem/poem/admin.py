from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.admin.sites import AdminSite
from django.views.decorators.cache import never_cache
from django.template.response import TemplateResponse

from Poem.poem.admin_interface.grmetrics import GroupOfMetricsAdmin
from Poem.poem.admin_interface.grprobes import GroupOfProbesAdmin
from Poem.poem.admin_interface.grprofiles import GroupOfProfilesAdmin
from Poem.poem.admin_interface.sitemetrics import *
from Poem.poem.admin_interface.siteprobes import *
from Poem.poem.admin_interface.siteprofile import *
from Poem.poem.admin_interface.userprofile import *
from Poem.poem.models import GroupOfMetrics, GroupOfProfiles
from Poem.poem.models import MetricInstance, Metric, Probe, Profile, UserProfile, VO, ServiceFlavour, GroupOfProfiles, CustUser
from Poem.settings import SAMLLOGINSTRING

from rest_framework.authtoken.models import Token
from rest_framework.authtoken.admin import TokenAdmin

import re

class MyAdminSite(AdminSite):
    @never_cache
    def index(self, request, extra_context=None):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return HttpResponseRedirect(request.path + 'poem')
            else:
                return HttpResponseRedirect(request.path + 'poem/profile')

    @never_cache
    def login(self, request, extra_context=None):
        extra_context = extra_context if extra_context else dict()
        extra_context.update(samlloginstring=SAMLLOGINSTRING)

        # If we are coming from /poem/public_probe/, /poem/public_probe/?,
        # /poem/public_probe/?all=, /poem/public_probe/?group=GROUP,
        # /poem/public_probe/?all=&group=GROUP and ask for individual
        # change_view for Probe, then proceed. Otherwise, we must authenticate.
        prev = request.META.get('HTTP_REFERER', None)
        if prev:
            r = re.search('public_probe/(\?)?(\?all\=)?([\&\?]group\=[\w\-]+)?$', prev)
            if r:
                context = dict(self.each_context(request))
                next_url = request.GET.get('next')
                objid = re.search('([0-9]+)', next_url)
                if objid:
                    objid = objid.group(1)
                    url = reverse('admin:poem_probe_change', args=(objid,))
                    if next_url == url:
                        return self._registry[Probe].change_view(request,
                                                                 objid,
                                                                 form_url='',
                                                                 extra_context=context)

        return super().login(request, extra_context)

    def app_index(self, request, app_label, extra_context=None):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                # Reorganize administration page by grouping type of data that
                # want to be administered:
                #   Poem = Metrics, Probes, Profiles
                #   Authnz = GroupOfMetrics, GroupOfProbes, GroupOfProfiles, Users
                #   Auth Tokens = Tokens
                app_list = self.get_app_list(request)
                authnz = dict(
                    name='Authentication and Authorization',
                    app_label='authnz',
                    app_url='/admin/poem',
                    has_module_perms=True,
                    models=list()
                )
                extract = set(['GroupOfProbes', 'GroupOfMetrics',
                               'GroupOfProfiles', 'CustUser'])

                for a in app_list:
                    if a['app_label'] == 'poem':
                        for m in a['models']:
                            if m['object_name'] in extract:
                                authnz['models'].append(m)
                        a['models'] = list(filter(lambda x: x['object_name']
                                                  not in extract, a['models']))

                app_list.append(authnz)
                order = ['poem', 'authnz', 'authtoken']

                app_list = sorted(app_list, key=lambda a: order.index(a['app_label']))

                extra_context = dict(
                    self.each_context(request),
                    app_list=app_list,
                )
                extra_context.update(extra_context or {})

                request.current_app = self.name

                return super().app_index(request, app_label, extra_context)
            else:
                return HttpResponseRedirect(request.path + 'profile')

    def get_urls(self):
        """
        Add public Probe changelist_view, that bypass permission checks implied
        in admin_view()
        """
        from django.urls import path
        urls = super().get_urls()
        my_urls = [path('poem/public_probe/', self.publicprobe_view)]
        return my_urls + urls

    def publicprobe_view(self, request):
        context = dict(self.each_context(request))
        return self._registry[Probe].changelist_view(request, extra_context=context)

    @never_cache
    def logout(self, request, extra_context=None):
        super().logout(request, extra_context=extra_context)
        return HttpResponseRedirect(reverse('admin:index'))


myadmin = MyAdminSite()

myadmin.register(Profile, ProfileAdmin)
myadmin.register(Probe, ProbeAdmin)
myadmin.register(Metric, MetricAdmin)
myadmin.register(GroupOfProfiles, GroupOfProfilesAdmin)
myadmin.register(GroupOfMetrics, GroupOfMetricsAdmin)
myadmin.register(GroupOfProbes, GroupOfProbesAdmin)
myadmin.register(CustUser, UserProfileAdmin)
myadmin.register(Token, TokenAdmin)
