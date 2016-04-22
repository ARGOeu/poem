from django.contrib import admin
from django.contrib.auth.models import Group
from Poem.poem.models import GroupOfMetrics, GroupOfProfiles
from Poem.poem.admin_interface.grmetrics import GroupOfMetricsAdmin
from Poem.poem.admin_interface.grprofiles import GroupOfProfilesAdmin
from Poem.poem.admin_interface.grprobes import GroupOfProbesAdmin
from Poem.poem.models import MetricInstance, Metric, Probe, Profile, UserProfile, VO, ServiceFlavour, GroupOfProfiles, CustUser

from Poem.poem.admin_interface.userprofile import *
from Poem.poem.admin_interface.siteprofile import *
from Poem.poem.admin_interface.siteprobes import *
from Poem.poem.admin_interface.sitemetrics import *

admin.site.unregister(Group)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Probe, ProbeAdmin)
admin.site.register(Metric, MetricAdmin)
admin.site.register(GroupOfProfiles, GroupOfProfilesAdmin)
admin.site.register(GroupOfMetrics, GroupOfMetricsAdmin)
admin.site.register(GroupOfProbes, GroupOfProbesAdmin)
admin.site.register(CustUser, UserProfileAdmin)
