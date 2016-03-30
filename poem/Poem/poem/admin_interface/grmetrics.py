from django.contrib import admin
from django.forms import ModelForm
from django.contrib.auth.models import Permission
from django.contrib.auth.admin import GroupAdmin
from Poem.poem.admin_interface.formmodel import MyModelMultipleChoiceField, MyFilteredSelectMultiple, MySelect
from Poem.poem.models import GroupOfMetrics, Metrics

class GroupOfMetricsForm(ModelForm):
    class Meta:
        model = GroupOfMetrics
    qs = Permission.objects.filter(codename__startswith='metrics')
    permissions = MyModelMultipleChoiceField(queryset=qs,
                                             widget=MySelect,
                                             help_text='Permission given to user members of the group across chosen metrics',
                                             ftype='permissions')
    permissions.empty_label = '----------------'
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
                 ('Settings', {'fields': ['permissions', 'metrics']})]
