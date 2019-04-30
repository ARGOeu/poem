from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.forms import ModelForm, CharField, Textarea, ValidationError, \
    BooleanField
from django.forms.widgets import TextInput
from django.urls import reverse
from django.utils.html import format_html
import json
import reversion
from reversion.models import Version, Revision
from reversion_compare.admin import CompareVersionAdmin
from tenant_schemas.utils import get_public_schema_name, schema_context

from Poem.poem.models import Metric
from Poem.poem_super_admin.models import Probe, ExtRevision
from Poem.tenants.models import Tenant


class ProbeAddForm(ModelForm):
    """
    Connects profile attributes to autocomplete widget (:py:mod:`poem.widgets`).
    Also adds media and does basic sanity checking for input.
    """
    new_version = BooleanField(help_text='Create version for changes',
                               required=False,
                               initial=True)

    name = CharField(help_text='Name of this probe.',
                     max_length=100,
                     widget=TextInput(attrs={'maxlength': 100, 'size': 45}),
                     label='Name')
    repository = CharField(help_text='Probe repository URL',
                           max_length=100,
                           widget=TextInput(attrs={'maxlength': 100,
                                                   'size': 61,
                                                   'type': 'url'}),
                           label='Repository')
    docurl = CharField(help_text='Documentation URL',
                       max_length=100,
                       widget=TextInput(attrs={'type': 'url',
                                               'maxlength': 100,
                                               'size': 61}),
                       label='Documentation')
    comment = CharField(help_text='Short comment about this version.',
                        widget=Textarea(attrs={
                            'style': 'width:500px;height:100px'}),
                        label='Comment')
    version = CharField(help_text='Version of the probe.',
                        max_length=28,
                        widget=TextInput(attrs={'maxlength': 28, 'size': 45}),
                        label='Version')
    description = CharField(help_text='Free text description outlining the '
                                      'purpose of this probe.',
                            widget=Textarea(attrs={
                                'style': 'width:500px;height:100px'}))
    user = CharField(help_text='User that added the probe',
                     max_length=64,
                     required=False)
    datetime = CharField(help_text='Time when probe is added',
                         max_length=64,
                         required=False)

    def clean(self):
        cleaned_data = super().clean()
        new_ver = cleaned_data['new_version']
        ver = cleaned_data['version']
        name = cleaned_data['name']

        try:
            probe = Probe.objects.get(name=name)
            if probe.version == ver and new_ver:
                raise ValidationError("Version number should be raised")
        except Probe.DoesNotExist:
            pass

        return cleaned_data


class ProbeChangeForm(ProbeAddForm):
    """
    Form rendered on change_view and derived from ProbeAddForm with name field
    kept readonly. If user wants to change the name of probe, he must create
    new one.
    """
    name = CharField(help_text='Name of this probe.',
                     max_length=100,
                     widget=TextInput(attrs={'maxlength': 100,
                                             'size': 45,
                                             'readonly': 'readonly'}),
                     label='Name')


class ProbeAdmin(CompareVersionAdmin, admin.ModelAdmin):
    """
    Probe admin core class that customizes its look and feel.
    """
    class Media:
        css = {"all": ("/poem_media/css/siteprobes.css",)}

    def num_versions(self, obj):
        num = ExtRevision.objects.filter(probeid=obj.id).count()
        return format_html(
            '<a href="{0}">{1}</a>',
            reverse('admin:poem_super_admin_probe_history',
                    args=(obj.id,)),
            num)
    num_versions.short_description = '# versions'

    list_display = ('name', 'num_versions', 'description')
    search_fields = ('name',)
    actions = None
    list_per_page = 20

    change_list_template = ''
    object_history_template = ''
    compare_template = ''

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.form = ProbeChangeForm
            self.fieldsets = (
                (None, {'classes': ['infoone'], 'fields': (
                    ('name', 'version', 'new_version',),
                    'datetime', 'user', )}),
                (None, {'classes': ['infotwo'], 'fields': (
                    'repository', 'docurl', 'description', 'comment',)}),
            )
            self.readonly_fields = ('user', 'datetime')
        else:
            self.form = ProbeAddForm
            self.fieldsets = (
                (None, {'classes': ['infoone'], 'fields': (
                    ('name', 'version',),)}),
                (None, {'classes': ['infotwo'], 'fields': (
                    'repository', 'docurl', 'description', 'comment', )}),
            )
            self.readonly_fields = ()
        return super(ProbeAdmin, self).get_form(request, obj=None, **kwargs)

    @reversion.create_revision()
    def save_model(self, request, obj, form, change):
        """
        In case new_version button is ticked, the new revision is created;
        in case that new_version button IS NOT ticked, there is no new
        revision created, only the data in Probe table in db is updated.
        """
        if request.user.is_superuser:
            obj.user = request.user.username
            if form.cleaned_data['new_version'] and change or not change:
                obj.save()
            elif not form.cleaned_data['new_version'] and change:
                version = Version.objects.get_for_object(obj)
                pk = version[0].object_id
                pk0 = version[0].id
                data = json.loads(Version.objects.get(pk=pk0).serialized_data)
                new_serialized_field = {
                    'name': form.cleaned_data['name'],
                    'version': form.cleaned_data['version'],
                    'description': form.cleaned_data['description'],
                    'comment': form.cleaned_data['comment'],
                    'repository': form.cleaned_data['repository'],
                    'docurl': form.cleaned_data['docurl'],
                    'user': obj.user
                }
                data[0]['fields'] = new_serialized_field
                Version.objects.filter(pk=pk0).update(
                    serialized_data=json.dumps(data)
                )
                Probe.objects.filter(pk=pk).update(**new_serialized_field)
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

    def has_change_permission(self, request, obj=None):
        return True

    @transaction.atomic()
    def delete_model(self, request, obj):
        schemas = list(Tenant.objects.all().values_list('schema_name',
                                                        flat=True))
        schemas.remove(get_public_schema_name())

        ct = ContentType.objects.get_for_model(obj)
        lver = Version.objects.filter(object_id=obj.id, content_type_id=ct.id)

        for schema in schemas:
            with schema_context(schema):
                for v in lver:
                    Revision.objects.filter(id=v.revision_id).delete()

                m = Metric.objects.filter(probeversion=obj.nameversion)
                if len(m) > 0:
                    m.update(probeversion='')

        return super(ProbeAdmin, self).delete_model(request, obj)

    def revision_view(self, request, object_id, version_id, extra_context=None):
        """
        Override original view to remove original title
        """
        currev = Version.objects.get(pk=version_id)
        datecreated = Revision.objects.get(pk=version_id).date_created

        new_context = {'title': currev.object_repr}
        if extra_context:
            extra_context.update({'cursel': currev.object_repr,
                                  'datecreated': datecreated})
        else:
            extra_context = {'cursel': currev.object_repr,
                             'datecreated': datecreated}
        extra_context.update(new_context)

        return self._reversion_revisionform_view(
            request,
            currev,
            self._reversion_get_template_list("revision_form.html"),
            extra_context,
        )

    def history_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or dict()
        if request.user.is_authenticated:
            extra_context.update(dict(include_history_link=True))
        return super().history_view(request, object_id,
                                    extra_context=extra_context)


reversion.register(Probe, exclude=["nameversion", "datetime"])