
from ajax_select import make_ajax_field
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.forms import ModelForm, Form, CharField, ModelChoiceField, \
    ValidationError, formset_factory
from django.forms.models import BaseInlineFormSet
from django.forms.widgets import TextInput, Select
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext as _
import json
import modelclone
from Poem.poem_super_admin.models import MetricTemplate, \
    MetricTemplateAttribute, MetricTemplateConfig, MetricTemplateDependency, \
    MetricTemplateFiles, MetricTemplateFileParameter, MetricTemplateFlags, \
    MetricTemplateParameter, MetricTemplateParent, \
    MetricTemplateProbeExecutable, MetricTemplateType
import reversion
from reversion.models import Version, Revision
from reversion_compare.admin import CompareVersionAdmin


class SharedInfo:
    def __init__(self, requser=None, grname=None, metrictype=None):
        if requser:
            self.__class__.user = requser
        if grname:
            self.__class__.group = grname
        if metrictype:
            self.__class__.metrictype = metrictype

    def get_metrictype(self):
        if getattr(self.__class__, 'metrictype', None):
            return self.__class__.metrictype
        else:
            return None

    def get_user(self):
        if getattr(self.__class__, 'user', None):
            return self.__class__.user
        else:
            return None


class RevisionTemplateTwoForm(Form):
    """
    Mimics the inlines with two fields.
    """
    key = CharField(label='key')
    value = CharField(label='value')


class RevisionTemplateOneForm(Form):
    """
    Mimics the inline with one field.
    """
    value = CharField(label='value')


class RevisionTemplateMetricForm(Form):
    """
    Mimics the adminform.
    """
    def __init__(self, *args, **kwargs):
        super(RevisionTemplateMetricForm, self).__init__(*args, **kwargs)
        self.fields['group'].empty_label = None
        self.fields['tag'].empty_label = None
        self.fields['mtype'].empty_label = None

    name = CharField(max_length=255, label='Name', help_text='Metric name')
    probeversion = make_ajax_field(MetricTemplate, 'probeversion',
                                   'hintsprobes', label='Probe', required=False,
                                   help_text='Probe name and version')
    qs = MetricTemplateType.objects.all()
    mtype = ModelChoiceField(queryset=qs, widget=Select(), label='Type',
                             help_text='Metric is of given type')


class MetricAddForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(MetricAddForm, self).__init__(*args, **kwargs)
        self.fields['mtype'].empty_label = None

    class Meta:
        labels = {
            'mtype': _('Type'),
        }
        help_texts = {
            'mtype': _('Metric is of given type'),
        }

    name = CharField(max_length=255, label='Name', help_text='Metric name')
    probeversion = make_ajax_field(MetricTemplate, 'probeversion',
                                   'hintsprobes', required=False, label='Probe',
                                   help_text='Probe name and version')

    def clean(self):
        try:
            metrictype = self.cleaned_data.get('mtype')
            SharedInfo(metrictype=metrictype)
        except KeyError:
            raise ValidationError('')
        else:
            super(MetricAddForm, self).clean()
            return self.cleaned_data


class MetricChangeForm(MetricAddForm):
    def __init__(self, *args, **kwargs):
        sh = SharedInfo()
        self.user = sh.get_user()
        super(MetricChangeForm, self).__init__(*args, **kwargs)

    class Meta:
        labels = {
            'mtype': _('Type'),
        }
        help_texts = {
            'mtype': _('Metric is of given type'),
        }


class MetricAttributeForm(ModelForm):
    key = CharField(label='key')
    value = CharField(label='value', required=False)

    def clean(self):
        update_field('attribute', self.cleaned_data, MetricTemplateAttribute)

        return super(MetricAttributeForm, self).clean()


class MetricAttributeInline(admin.TabularInline):
    model = MetricTemplateAttribute
    verbose_name = 'Attribute'
    verbose_name_plural = 'Attributes'
    form = MetricAttributeForm
    template = 'admin/edit_inline/tabular-attrs.html'
    extra = 1

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        return True


class MetricParameterForm(ModelForm):
    key = CharField(label='key')
    value = CharField(label='value', required=False)

    def clean(self):
        update_field('parameter', self.cleaned_data, MetricTemplateParameter)

        return super(MetricParameterForm, self).clean()


class MetricParameterInline(admin.TabularInline):
    model = MetricTemplateParameter
    verbose_name = 'Parameter'
    verbose_name_plural = 'Parameter'
    form = MetricParameterForm
    template = 'admin/edit_inline/tabular-attrs.html'
    extra = 1

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        return True


class MetricFilesForm(ModelForm):
    key = CharField(label='key')
    value = CharField(label='value', required=False)

    def clean(self):
        update_field('files', self.cleaned_data, MetricTemplateFiles)

        return super(MetricFilesForm, self).clean()


class MetricFilesInline(admin.StackedInline):
    model = MetricTemplateFiles
    verbose_name = 'File attributes'
    verbose_name_plural = 'File attributes'
    form = MetricFilesForm
    template = 'admin/edit_inline/tabular-attrs.html'
    extra = 1

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        return True


def isvalid_metricflags(data):
    """
        Validation for Passive metric types. There should be at least
        key = PASSIVE and value = 1 defined.
    """
    sh = SharedInfo()
    metric_type = sh.get_metrictype().name.lower()

    if metric_type == 'passive':
        keys_values = [(d.get('key', None), d.get('value', None)) for d in data]
        passive_found = [
            (k, v) for k, v in keys_values if k and k.lower() == 'passive'
        ]
        if not passive_found:
            raise ValidationError('Missing PASSIVE key')
        elif passive_found[0][1] not in ['1', 'True']:
            raise ValidationError('PASSIVE key should be set to 1')

        return True


class MetricFlagsInlineFormset(BaseInlineFormSet):
    def clean(self):
        super().clean()
        data = list()
        for form in self.forms:
            data.append(form.cleaned_data)
        return isvalid_metricflags(data)


class MetricFlagsForm(ModelForm):
    key = CharField(label='key')
    value = CharField(label='value', required=False)

    def clean(self):
        update_field('flags', self.cleaned_data, MetricTemplateFlags)

        return super(MetricFlagsForm, self).clean()


class MetricFlagsInline(admin.TabularInline):
    model = MetricTemplateFlags
    verbose_name = 'Flags'
    verbose_name_plural = 'Flags'
    form = MetricFlagsForm
    formset = MetricFlagsInlineFormset
    template = 'admin/edit_inline/tabular-attrs.html'
    extra = 1

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        return True


class MetricDependencyForm(ModelForm):
    key = CharField(label='key')
    value = CharField(label='value', required=False)

    def clean(self):
        update_field('dependency', self.cleaned_data, MetricTemplateDependency)

        return super(MetricDependencyForm, self).clean()


class MetricDependencyInline(admin.TabularInline):
    model = MetricTemplateDependency
    verbose_name = 'Dependency'
    verbose_name_plural = 'Dependency'
    form = MetricDependencyForm
    template = 'admin/edit_inline/tabular-attrs.html'
    extra = 1

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        return True


class MetricConfigForm(ModelForm):
    key = CharField(label='key',
                    widget=TextInput(attrs={'readonly': 'readonly'}))
    value = CharField(label='value')

    def clean(self):
        update_field('config', self.cleaned_data, MetricTemplateConfig)

        return super(MetricConfigForm, self).clean()


def isvalid_metricconfig(data):
    """
        Validation for Active metric types. All keys need to have values.
    """
    sh = SharedInfo()
    metric_type = sh.get_metrictype().name.lower()

    if metric_type == 'active':
        needed_keys = ['interval', 'maxCheckAttempts', 'path', 'retryInterval',
                       'timeout']

        found_keys = set([d.get('key', None) for d in data])
        diff = set(needed_keys).difference(found_keys)
        if diff:
            raise ValidationError('Missing fields %s' % ', '.join(diff))

        missing_values = list()
        for d in data:
            key = d.get('key', 0)
            if key and key in needed_keys:
                v = d.get('value', 0)
                if not v:
                    missing_values.append(key)

        if missing_values:
            raise ValidationError(
                'Missing values for fields %s' % ', '.join(missing_values)
            )

    return True


class MetricConfigInlineAddFormSet(BaseInlineFormSet):
    """
    Formset that manually populates fields for form.
    """
    def __init__(self, *args, **kwargs):
        kwargs['initial'] = [
            {'key': 'interval'}, {'key': 'maxCheckAttempts'}, {'key': 'path'},
            {'key': 'retryInterval'}, {'key': 'timeout'},
        ]
        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()
        data = list()
        for form in self.forms:
            data.append(form.cleaned_data)
        return isvalid_metricconfig(data)


class MetricConfigInlineChangeFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        data = list()
        for form in self.forms:
            data.append(form.cleaned_data)
        isvalid_metricconfig(data)


class MetricConfigInline(admin.TabularInline):
    model = MetricTemplateConfig
    verbose_name = 'Config'
    verbose_name_plural = 'Config'
    form = MetricConfigForm
    formset = MetricConfigInlineChangeFormSet
    template = 'admin/edit_inline/tabular-attrs.html'

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True


class MetricFileParameterForm(ModelForm):
    key = CharField(label='key')
    value = CharField(label='value', required=False)

    def clean(self):
        update_field('fileparameter', self.cleaned_data,
                     MetricTemplateFileParameter)

        return super(MetricFileParameterForm, self).clean()


class MetricFileParameterInline(admin.TabularInline):
    model = MetricTemplateFileParameter
    verbose_name = 'File parameters'
    verbose_name_plural = 'File parameters'
    form = MetricFileParameterForm
    template = 'admin/edit_inline/tabular-attrs.html'
    extra = 1

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        return True


class MetricParentForm(ModelForm):
    value = make_ajax_field(MetricTemplate, 'name', 'hintsmetrictemplates')

    def clean(self):
        update_field('parent', self.cleaned_data, MetricTemplateParent)

        return super(MetricParentForm, self).clean()


class MetricParentInline(admin.TabularInline):
    model = MetricTemplateParent
    verbose_name = 'Parent metric'
    verbose_name_plural = 'Parent metric'
    form = MetricParentForm
    template = 'admin/edit_inline/tabular-attrs-exec.html'
    max_num = 1
    can_delete = False

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True


class MetricProbeExecutableForm(ModelForm):
    value = CharField(max_length=255)

    def clean(self):
        update_field('probeexecutable', self.cleaned_data,
                     MetricTemplateProbeExecutable)

        return super(MetricProbeExecutableForm, self).clean()


class MetricProbeExecutableInline(admin.TabularInline):
    model = MetricTemplateProbeExecutable
    verbose_name = 'Probe executable'
    verbose_name_plural = 'Probe executable'
    form = MetricProbeExecutableForm
    template = 'admin/edit_inline/tabular-attrs-exec.html'
    max_num = 1
    can_delete = False

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True


class MetricAdmin(CompareVersionAdmin, modelclone.ClonableModelAdmin):
    class Media:
        css = {"all": ("/poem_media/css/sitemetrics.css",)}

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

    list_display = ('name', 'probeversion_url')
    fieldsets = ((None, {'classes': ['tagging'],
                         'fields': (('name', 'probeversion', 'mtype'),)}),)
    inlines = (MetricProbeExecutableInline, MetricConfigInline,
               MetricAttributeInline, MetricDependencyInline,
               MetricParameterInline, MetricFlagsInline, MetricFilesInline,
               MetricFileParameterInline, MetricParentInline,)
    search_fields = ('name',)
    actions = None
    ordering = ('name',)
    list_per_page = 30

    change_list_template = ''
    object_history_template = ''
    compare_template = ''
    change_form_template = ''

    def get_formsets_with_inlines(self, request, obj=None):
        """
        Control the extra attr value for MetricConfigInline. For change and
        clone view it is set to 0 as we don't want extra empty fields additional
        to ones populated with values from model. For add view we explicitly set
        to 5 and manually populate with MetricConfigInlineFormset that set it to
        needed static keys.
        """
        for inline in self.get_inline_instances(request, obj):
            if isinstance(inline, MetricConfigInline):
                if (request.path.endswith('change/')
                        or request.path.endswith('clone/')):
                    inline.extra = 0
                    inline.formset = MetricConfigInlineChangeFormSet
                else:
                    inline.extra = 5
                    inline.formset = MetricConfigInlineAddFormSet
            yield inline.get_formset(request, obj), inline

    def clone_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context.update({
            'clone_view': True,
            'metric_id': object_id,
            'metric_name': str(MetricTemplate.objects.get(pk=object_id)),
            'original': 'Clone',
            'title': 'Clone'})
        return super(MetricAdmin, self).clone_view(request, object_id,
                                                   form_url, extra_context)

    def get_form(self, request, obj=None, **kwargs):
        rquser = SharedInfo(requser=request.user)
        if obj:
            self.form = MetricChangeForm
        else:
            self.form = MetricAddForm
        return super(MetricAdmin, self).get_form(request, obj=None, **kwargs)

    @transaction.atomic()
    def delete_model(self, request, obj):
        ct = ContentType.objects.get_for_model(obj)
        lver = Version.objects.filter(object_id=obj.id,
                                      content_type_id=ct.id)
        ids = map(lambda x: x.revision_id, lver)
        Revision.objects.filter(pk__in=ids).delete()

        # Don't delete metrics for now from Metrics model that is needed by
        # GroupAdmin
        # Metrics.objects.get(name=obj.name).delete()

        return super(MetricAdmin, self).delete_model(request, obj)

    @reversion.create_revision()
    def save_model(self, request, obj, form, change):
        if obj.probeversion:
            obj.probekey = Version.objects.get(
                object_repr__exact=obj.probeversion
            )
        if request.path.endswith('/clone/'):
            import re
            cloned_metric = re.search(
                '([0-9]*)/change/clone', request.path
            ).group(1)
            from_metric = MetricTemplate.objects.get(pk=cloned_metric)
            reversion.set_user(request.user)
            reversion.set_comment('Derived from %s' % from_metric)
            obj.cloned = cloned_metric
        else:
            obj.cloned = ''
        if request.user.is_superuser:
            obj.save()
            return
        else:
            raise PermissionDenied()

    def get_row_css(self, obj, index):
        if not obj.valid:
            return 'row_red red%d' % index
        return ''

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        else:
            return False

    def revision_view(self, request, object_id, version_id, extra_context=None):
        """
        Build custom formsets based on forms.Form and pass them to template
        context. Forms will be populated with the data from corresponding
        Version object bypassing ModelAdmin logic and mimicking ModelAdmin
        change_view with inlines.

        Also we do not call superclass method but rather override it since
        we're not interested in original "revert to" behaviour. We just care for
        view with proper form data.
        """
        version_obj = Version.objects.get(pk=version_id)
        currev = version_obj.revision.date_created
        data = json.loads(Version.objects.get(pk=version_id).serialized_data)[0]['fields']
        order = [
            (inline_name.__name__, inline_name.verbose_name) for inline_name
            in self.inlines
        ]

        version_data_order = list()
        custom_formsets = list()
        verbose_name = {'probeexecutable': 'Probe executable',
                        'attribute': 'Attributes',
                        'config': 'Config',
                        'dependency': 'Dependency',
                        'parameter': 'Parameter',
                        'flags': 'Flags',
                        'files': 'File attributes',
                        'fileparameter': 'File parameters',
                        'parent': 'Parent metric'}

        for e in order:
            for d in data:
                if e[0].lower().startswith('metric'+d.lower()):
                    value = json.loads(data[d]) if data[d] else ''
                    version_data_order.append({d: value})

        for version in version_data_order:
            element = [(k, v) for (k, v) in version.items()]
            values = element[0]
            settings = values[1]
            if values[0] == 'probeexecutable' or values[0] == 'parent':
                factory = formset_factory(
                    RevisionTemplateOneForm, can_delete=False, extra=1
                )
                v = settings[0] if settings else ''
                formset = factory(initial=[{'value': v}], prefix=values[0])
                formset.verbose_name = verbose_name[values[0]]
            else:
                initial = list()
                factory = formset_factory(
                    RevisionTemplateTwoForm, can_delete=True, extra=1
                )
                for s in settings:
                    k, v = s.split(' ', 1)
                    initial.append({'key': k, 'value': v})
                formset = factory(initial=initial, prefix=values[0])
                formset.verbose_name = verbose_name[values[0]]
            custom_formsets.append(formset)

        undisplay_passive = list(['probeexecutable', 'attribute', 'dependency',
                                  'config', 'parameter', 'files',
                                  'fileparameter']);

        # only flags and parent form for Passive metric type
        # mtype = 2 (Passive) is hardcoded in fixture
        if data['mtype'] == 2:
            custom_formsets = filter(
                lambda f: f.prefix not in undisplay_passive, custom_formsets
            )

        custom_adminform = RevisionTemplateMetricForm(
            initial={'name': data['name'],
                     'probeversion': data['probeversion'],
                     'mtype': data['mtype']})

        new_context = {'cursel': currev,
                       'custom_formsets': custom_formsets,
                       'custom_adminform': custom_adminform,
                       'title': "{} on {}".format(
                           version_obj.object_repr,
                           currev.strftime('%d/%m/%y %H:%m')
                       )}
        if extra_context:
            extra_context.update(new_context)
        else:
            extra_context = new_context

        # override revert() method as we don't really care if original object
        # for revision exists in DB. Since we are copying revisions for derived
        # metric on clone, original object for each revision might not even
        # exist in DB.
        version_obj.revision.revert = lambda **kw: True

        return self._reversion_revisionform_view(
            request,
            version_obj,
            self._reversion_get_template_list("revision_form.html"),
            extra_context,
        )

    def has_change_permission(self, request, obj=None):
        return True

    def history_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or dict()
        if request.user.is_authenticated:
            extra_context.update(dict(include_history_link=True))
        return super().history_view(request,
                                    object_id,
                                    extra_context=extra_context)


def update_field(field, formdata, model):
    try:
        try:
            newentry = '{0} {1}'.format(formdata['key'], formdata['value'])
        except KeyError:
            newentry = '{0}'.format(formdata['value'])

        deleted = bool(formdata.get('DELETE', False))
        objs = model.objects.filter(
            metrictemplate__exact=formdata['metrictemplate']
        )
        objfield = eval("formdata['metrictemplate'].%s" % field)

        fielddata = None
        if deleted and objfield:
            fielddata = json.loads(objfield)
            if formdata['id']:
                index = list(objs).index(formdata['id'])
                if index in fielddata:
                    del fielddata[index]
        else:
            if objfield:
                fielddata = json.loads(objfield)
                if formdata['id']:
                    index = list(objs).index(formdata['id'])
                    fielddata[index] = newentry
                else:
                    fielddata.append(newentry)
            else:
                fielddata = list([newentry])

        codestr = \
            """formdata['metrictemplate'].%s = json.dumps(fielddata)""" % field
        exec(codestr)

    except KeyError as e:
        raise ValidationError('')

reversion.register(MetricTemplate, exclude=["cloned"])
