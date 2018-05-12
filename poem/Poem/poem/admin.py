from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.admin.sites import AdminSite
from django.views.decorators.cache import never_cache
from Poem.poem.models import GroupOfMetrics, GroupOfProfiles
from Poem.poem.admin_interface.grmetrics import GroupOfMetricsAdmin
from Poem.poem.admin_interface.grprofiles import GroupOfProfilesAdmin
from Poem.poem.admin_interface.grprobes import GroupOfProbesAdmin
from Poem.poem.models import MetricInstance, Metric, Probe, Profile, UserProfile, VO, ServiceFlavour, GroupOfProfiles, CustUser

from Poem.poem.admin_interface.userprofile import *
from Poem.poem.admin_interface.siteprofile import *
from Poem.poem.admin_interface.siteprobes import *
from Poem.poem.admin_interface.sitemetrics import *
from Poem.settings import SAMLLOGINSTRING

class MyAdminSite(AdminSite):
    @never_cache
    def index(self, request, extra_context=None):
        if request.user.is_authenticated():
            if request.user.is_superuser:
                return HttpResponseRedirect(request.path + 'poem')
            else:
                return HttpResponseRedirect(request.path + 'poem/profile')

    @never_cache
    def login(self, request, extra_context=None):
        extra_context = extra_context if extra_context else dict()
        extra_context.update(samlloginstring=SAMLLOGINSTRING)
        return super(MyAdminSite, self).login(request, extra_context)


    def app_index(self, request, app_label, extra_context=None):
        if request.user.is_authenticated():
            if request.user.is_superuser:
                return super(MyAdminSite, self).app_index(request, app_label, extra_context)
            else:
                return HttpResponseRedirect(request.path + 'profile')

    @never_cache
    def logout(self, request, extra_context=None):
        super(MyAdminSite,self).logout(request, extra_context=extra_context)
        return HttpResponseRedirect(reverse('admin:index'))


myadmin = MyAdminSite()

myadmin.register(Profile, ProfileAdmin)
myadmin.register(Probe, ProbeAdmin)
myadmin.register(Metric, MetricAdmin)
myadmin.register(GroupOfProfiles, GroupOfProfilesAdmin)
myadmin.register(GroupOfMetrics, GroupOfMetricsAdmin)
myadmin.register(GroupOfProbes, GroupOfProbesAdmin)
myadmin.register(CustUser, UserProfileAdmin)
