from django.contrib import admin
from django.forms import ModelForm
from django.contrib.auth.models import Permission
from django.contrib.auth.admin import GroupAdmin
from Poem.poem.models import GroupOfProbes, Probe
from Poem.poem.admin_interface.formmodel import MyModelMultipleChoiceField, MySelect, MyFilteredSelectMultiple

class GroupOfProbesAdminForm(ModelForm):
    class Meta:
        model = GroupOfProbes
    qs = Permission.objects.filter(codename__startswith='probe')
    permissions = MyModelMultipleChoiceField(queryset=qs,
                                             widget=MySelect,
                                             help_text='Permission given to user members of the group across chosen probes',
                                             ftype='permissions')
    permissions.empty_label = '----------------'
    qs = Probe.objects.filter(groupofprobes__id__isnull=True).order_by('name')
    profiles = MyModelMultipleChoiceField(queryset=qs,
                                          required=False,
                                          widget=MyFilteredSelectMultiple('profiles', False), ftype='profiles')

class GroupOfProbesAdmin(GroupAdmin):
    class Media:
        css = { "all" : ("/poem_media/css/poem_profile.custom.css",) }

    form = GroupOfProbesAdminForm
    search_field = ()
    filter_horizontal=('probes',)
    fieldsets = [(None, {'fields': ['name']}),
                 ('Settings', {'fields': ['permissions', 'probes']})]

