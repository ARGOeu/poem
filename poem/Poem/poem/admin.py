from django.http import HttpResponseRedirect
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.admin.sites import AdminSite
from Poem.poem.models import GroupOfMetrics, GroupOfProfiles
from Poem.poem.admin_interface.grmetrics import GroupOfMetricsAdmin
from Poem.poem.admin_interface.grprofiles import GroupOfProfilesAdmin
from Poem.poem.admin_interface.grprobes import GroupOfProbesAdmin
from Poem.poem.models import MetricInstance, Metric, Probe, Profile, UserProfile, VO, ServiceFlavour, GroupOfProfiles, CustUser

from Poem.poem.admin_interface.userprofile import *
from Poem.poem.admin_interface.siteprofile import *
from Poem.poem.admin_interface.siteprobes import *
from Poem.poem.admin_interface.sitemetrics import *

class MyAdminSite(AdminSite):
    def index(self, request, extra_context=None):
        if request.user.is_superuser:
            return HttpResponseRedirect(request.path + 'poem')
        else:
            return HttpResponseRedirect(request.path + 'poem/profile')

myadmin = MyAdminSite()

myadmin.register(Profile, ProfileAdmin)
myadmin.register(Probe, ProbeAdmin)
myadmin.register(Metric, MetricAdmin)
myadmin.register(GroupOfProfiles, GroupOfProfilesAdmin)
myadmin.register(GroupOfMetrics, GroupOfMetricsAdmin)
myadmin.register(GroupOfProbes, GroupOfProbesAdmin)
myadmin.register(CustUser, UserProfileAdmin)
