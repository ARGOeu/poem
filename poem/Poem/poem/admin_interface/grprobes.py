from django.contrib import admin
from django.forms import ModelForm
from django.contrib.auth.models import Permission
from django.contrib.auth.admin import GroupAdmin
from Poem.poem.models import GroupOfProbes, Probe
from Poem.poem.admin_interface.formmodel import MyModelMultipleChoiceField, MySelect, MyFilteredSelectMultiple

class GroupOfProbesAdminForm(ModelForm):
    class Meta:
        model = GroupOfProbes
    qs = Probe.objects.filter(groupofprobes__id__isnull=True).order_by('nameversion')
    probes = MyModelMultipleChoiceField(queryset=qs,
                                        required=False,
                                        widget=MyFilteredSelectMultiple('probes', False), ftype='probes')


class GroupOfProbesAdmin(GroupAdmin):
    class Media:
        css = { "all" : ("/poem_media/css/grprobes.css",) }

    form = GroupOfProbesAdminForm
    search_field = ()
    filter_horizontal=('probes',)
    fieldsets = [(None, {'fields': ['name']}),
                 ('Settings', {'fields': ['probes']})]

    def save_model(self, request, obj, form, change):
        obj.save()
        perm = Permission.objects.get(codename__startswith='probe')
        obj.permissions.add(perm)
