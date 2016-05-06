from django.contrib import admin
from django.forms import ModelForm
from django.contrib.auth.models import Permission
from django.contrib.auth.admin import GroupAdmin
from Poem.poem.models import GroupOfProfiles, Profile
from Poem.poem.admin_interface.formmodel import MyModelMultipleChoiceField, MySelect, MyFilteredSelectMultiple

class GroupOfProfilesAdminForm(ModelForm):
    class Meta:
        model = GroupOfProfiles
    qs = Permission.objects.filter(codename__startswith='profile')
    permissions = MyModelMultipleChoiceField(queryset=qs,
                                             widget=MySelect,
                                             help_text='Permission given to user members of the group across chosen profiles',
                                             ftype='permissions')
    permissions.empty_label = '----------------'
    qs = Profile.objects.filter(groupofprofiles__id__isnull=True).order_by('name')
    profiles = MyModelMultipleChoiceField(queryset=qs,
                                          required=False,
                                          widget=MyFilteredSelectMultiple('profiles', False), ftype='profiles')

class GroupOfProfilesAdmin(GroupAdmin):
    class Media:
        css = { "all" : ("/poem_media/css/grprofiles.css",) }

    form = GroupOfProfilesAdminForm
    search_field = ()
    filter_horizontal=('profiles',)
    fieldsets = [(None, {'fields': ['name']}),
                 ('Settings', {'fields': ['permissions', 'profiles']})]
