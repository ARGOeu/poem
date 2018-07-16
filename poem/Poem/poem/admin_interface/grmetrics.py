from django.contrib import admin
from django.forms import ModelForm
from django.contrib.auth.models import Permission
from django.contrib.auth.admin import GroupAdmin
from Poem.poem.admin_interface.formmodel import MyModelMultipleChoiceField, MyFilteredSelectMultiple
from Poem.poem.models import GroupOfMetrics, Metrics


class GroupOfMetricsForm(ModelForm):
    qs = Metrics.objects.filter(groupofmetrics__id__isnull=True).order_by('name')
    metrics = MyModelMultipleChoiceField(queryset=qs,
                                         required=False,
                                         widget=MyFilteredSelectMultiple('metrics', False), ftype='metrics')


class GroupOfMetricsAdmin(GroupAdmin):
    class Media:
        css = { "all" : ("/poem_media/css/grmetrics.css",) }

    form = GroupOfMetricsForm
    search_field = ()
    filter_horizontal=('metrics',)
    fieldsets = [(None, {'fields': ['name']}),
                 ('Settings', {'fields': ['metrics']})]

    def save_model(self, request, obj, form, change):
        obj.save()
        perm = Permission.objects.get(codename__startswith='metrics')
        obj.permissions.add(perm)
