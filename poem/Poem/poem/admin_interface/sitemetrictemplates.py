from django.contrib import admin
from django.forms import ModelChoiceField, ModelForm, CharField
from django.forms.widgets import Select, TextInput
from django.utils.html import format_html
from django.urls import reverse
import json
from Poem.poem.models import GroupOfMetrics, Metric, MetricAttribute, \
    MetricConfig, MetricDependancy, MetricFiles, MetricFileParameter, \
    MetricFlags, MetricParameter, MetricParent, MetricProbeExecutable, \
    MetricType, Tags
from Poem.poem_super_admin.models import MetricTemplate, \
    MetricTemplateAttribute, MetricTemplateConfig, MetricTemplateDependency, \
    MetricTemplateFiles, MetricTemplateFileParameter, MetricTemplateFlags, \
    MetricTemplateParameter, MetricTemplateParent, \
    MetricTemplateProbeExecutable, MetricTemplateType
from reversion.models import Version


class MetricTemplateForm(ModelForm):
    name = CharField(max_length=255, label='Name', help_text='Metric name',
                     widget=TextInput(attrs={'readonly': 'readonly'}))
    probeversion = CharField(label='Probe', help_text='Probe name and version',
                             required=False,
                             widget=TextInput(attrs={'readonly': 'readonly'}))

    qs = MetricTemplateType.objects.all()
    mtype = ModelChoiceField(queryset=qs, label='Type',
                             help_text='Metric is of given type',
                             widget=Select(attrs={'disabled': 'disabled'}))


class MetricAttributeForm(ModelForm):
    key = CharField(label='key',
                    widget=TextInput(attrs={'readonly': 'readonly'}))
    value = CharField(label='value', required=False,
                      widget=TextInput(attrs={'readonly': 'readonly'}))


class MetricAttributeInline(admin.TabularInline):
    model = MetricTemplateAttribute
    verbose_name = 'Attribute'
    verbose_name_plural = 'Attributes'
    form = MetricAttributeForm
    template = 'admin/edit_inline/tabular-attrs.html'
    extra = 0

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True


class MetricParameterForm(ModelForm):
    key = CharField(label='key',
                    widget=TextInput(attrs={'readonly': 'readonly'}))
    value = CharField(label='value', required=False,
                      widget=TextInput(attrs={'readonly': 'readonly'}))


class MetricParameterInline(admin.TabularInline):
    model = MetricTemplateParameter
    verbose_name = 'Parameter'
    verbose_name_plural = 'Parameter'
    form = MetricParameterForm
    template = 'admin/edit_inline/tabular-attrs.html'
    extra = 0

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True


class MetricFilesForm(ModelForm):
    key = CharField(label='key',
                    widget=TextInput(attrs={'readonly': 'readonly'}))
    value = CharField(label='value', required=False,
                      widget=TextInput(attrs={'readonly': 'readonly'}))


class MetricFilesInline(admin.TabularInline):
    model = MetricTemplateFiles
    verbose_name = 'File attributes'
    verbose_name_plural = 'File attributes'
    form = MetricFilesForm
    template = 'admin/edit_inline/tabular-attrs.html'
    extra = 0

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True


class MetricFlagsForm(ModelForm):
    key = CharField(label='key',
                    widget=TextInput(attrs={'readonly': 'readonly'}))
    value = CharField(label='value', required=False,
                      widget=TextInput(attrs={'readonly': 'readonly'}))


class MetricFlagsInline(admin.TabularInline):
    model = MetricTemplateFlags
    verbose_name = 'Flags'
    verbose_name_plural = 'Flags'
    form = MetricFlagsForm
    template = 'admin/edit_inline/tabular-attrs.html'
    extra = 0

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True


class MetricDependencyForm(ModelForm):
    key = CharField(label='key',
                    widget=TextInput(attrs={'readonly': 'readonly'}))
    value = CharField(label='value', required=False,
                      widget=TextInput(attrs={'readonly': 'readonly'}))


class MetricDependencyInline(admin.TabularInline):
    model = MetricTemplateDependency
    verbose_name = 'Dependency'
    verbose_name_plural = 'Dependency'
    form = MetricDependencyForm
    template = 'admin/edit_inline/tabular-attrs.html'
    extra = 0

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True


class MetricConfigForm(ModelForm):
    key = CharField(label='key',
                    widget=TextInput(attrs={'readonly': 'readonly'}))
    value = CharField(label='value', required=False,
                      widget=TextInput(attrs={'readonly': 'readonly'}))


class MetricConfigInline(admin.TabularInline):
    model = MetricTemplateConfig
    verbose_name = 'Config'
    verbose_name_plural = 'Config'
    form = MetricConfigForm
    template = 'admin/edit_inline/tabular-attrs.html'
    extra = 0

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True


class MetricFileParameterForm(ModelForm):
    key = CharField(label='key',
                    widget=TextInput(attrs={'readonly': 'readonly'}))
    value = CharField(label='value', required=False,
                      widget=TextInput(attrs={'readonly': 'readonly'}))


class MetricFileParameterInline(admin.TabularInline):
    model = MetricTemplateFileParameter
    verbose_name = 'File parameters'
    verbose_name_plural = 'File parameters'
    form = MetricFileParameterForm
    template = 'admin/edit_inline/tabular-attrs.html'
    extra = 0

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True


class MetricParentForm(ModelForm):
    value = CharField(required=False,
                      widget=TextInput(attrs={'readonly': 'readonly'}))


class MetricParentInline(admin.TabularInline):
    model = MetricTemplateParent
    verbose_name = 'Parent metric'
    verbose_name_plural = 'Parent metric'
    form = MetricParentForm
    template = 'admin/edit_inline/tabular-attrs.html'
    extra = 0

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class MetricProbeExecutableForm(ModelForm):
    value = CharField(max_length=255,
                      widget=TextInput(attrs={'readonly': 'readonly'}))


class MetricProbeExecutableInline(admin.TabularInline):
    model = MetricTemplateProbeExecutable
    verbose_name = 'Probe executable'
    verbose_name_plural = 'Probe executable'
    form = MetricProbeExecutableForm
    template = 'admin/edit_inline/tabular-attrs.html'
    extra = 0

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


def create_inlines(model, data, metric):
    data = json.loads(data)
    if model == MetricProbeExecutable or model == MetricParent:
        model.objects.create(value=data[0],
                             metric=metric)
    else:
        for d in data:
            model.objects.create(key=d.split(' ')[0],
                                 value=d.split(' ')[1],
                                 metric=metric)


class MetricTemplateAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('/poem_media/css/sitemetrictemplates.css',)}

    def probeversion_url(self, obj):
        if obj and obj.probeversion and obj.probekey:
            return format_html(
                '<a href="{0}">{1}</a>',
                reverse('admin:poem_super_admin_probe_revision',
                        args=(obj.probekey.object_id,
                              obj.probekey.pk)),
                obj.probeversion)
        else:
            return None
    probeversion_url.short_description = 'Probeversion'

    def import_metric_templates(self, request, queryset):
        for query in queryset:
            mt = MetricType.objects.get(name=query.mtype)
            t = Tags.objects.get(name='Test')
            group = GroupOfMetrics.objects.get(name=request.tenant.name.upper())
            if query.probeversion:
                ver = Version.objects.get(object_repr=query.probeversion)
                m = Metric.objects.create(
                    name=query.name, mtype=mt, probeversion=query.probeversion,
                    probekey=ver, parent=query.parent, tag=t, group=group,
                    probeexecutable=query.probeexecutable, config=query.config,
                    attribute=query.attribute, dependancy=query.dependency,
                    flags=query.flags, files=query.files, parameter=query.parameter,
                    fileparameter=query.fileparameter
                )
                if query.config:
                    create_inlines(MetricConfig, query.config, m)
                if query.dependency:
                    create_inlines(MetricDependancy, query.dependency, m)
                if query.files:
                    create_inlines(MetricFiles, query.files, m)
                if query.parameter:
                    create_inlines(MetricParameter, query.parameter, m)
                if query.fileparameter:
                    create_inlines(MetricFileParameter, query.fileparameter, m)
                if query.attribute:
                    create_inlines(MetricAttribute, query.attribute, m)
                if query.probeexecutable:
                    create_inlines(MetricProbeExecutable, query.probeexecutable,
                                   m)
            else:
                m = Metric.objects.create(
                    name=query.name, mtype=mt, parent=query.parent,
                    flags=query.flags, tag=t, group=group
                )
            if query.parent:
                create_inlines(MetricParent, query.parent, m)
            if query.flags:
                create_inlines(MetricFlags, query.flags, m)
        if len(queryset) == 1:
            message_bit = '1 metric template has'
        else:
            message_bit = '%s metric templates have' % len(queryset)
        self.message_user(request, '%s been successfully imported.'
                          % message_bit)
    import_metric_templates.short_description = \
        'Import selected metric templates as metrics'

    list_display = ('name', 'probeversion_url',)
    form = MetricTemplateForm
    fieldsets = ((None, {'classes': ['tagging'],
                         'fields': (('name', 'probeversion', 'mtype'),)}),)
    inlines = (MetricProbeExecutableInline, MetricConfigInline,
               MetricAttributeInline, MetricDependencyInline,
               MetricParameterInline, MetricFlagsInline, MetricFilesInline,
               MetricFileParameterInline, MetricParentInline,)
    search_fields = ('name',)
    actions = ['import_metric_templates']
    ordering = ('name',)
    list_per_page = 30

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save'] = False
        return super().change_view(request, object_id, form_url,
                                   extra_context=extra_context)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
