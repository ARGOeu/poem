from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.admin.sites import AdminSite
from django.views.decorators.cache import never_cache
from Poem.poem.models import GroupOfMetrics, GroupOfProfiles
from Poem.poem.admin_interface.grmetrics import GroupOfMetricsAdmin
from Poem.poem.admin_interface.grprofiles import GroupOfProfilesAdmin
from Poem.poem.admin_interface.grprobes import GroupOfProbesAdmin
from Poem.poem.models import MetricInstance, Metric, Probe, Profile, UserProfile, VO, ServiceFlavour, GroupOfProfiles, CustUser
from Poem.settings import SAMLLOGINSTRING

from Poem.poem.admin_interface.userprofile import *
from Poem.poem.admin_interface.siteprofile import *
from Poem.poem.admin_interface.siteprobes import *
from Poem.poem.admin_interface.sitemetrics import *

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

        # If we are coming from /poem/public_probe/ and ask for individual
        # change_view for Probe, then proceed. Otherwise, we must authenticate.
        prev = request.META.get('HTTP_REFERER', None)
        if prev:
            if prev.endswith('public_probe/') or prev.endswith('public_probe/?all='):
                context = dict(self.each_context(request))
                next_url = request.GET.get('next')
                objid = re.search('([0-9]+)', next_url)
                if objid:
                    objid = objid.group(1)
                    url = reverse('admin:poem_probe_change', args=(objid,))
                    if next_url == url:
                        return self._registry[Probe].change_view(request, objid, form_url='', extra_context=context)

        return super().login(request, extra_context)

    def app_index(self, request, app_label, extra_context=None):
        if request.user.is_authenticated:
            if request.user.is_superuser:
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
