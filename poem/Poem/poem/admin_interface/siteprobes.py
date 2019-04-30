from django.forms import ModelForm, CharField, Textarea
from django.forms.widgets import TextInput
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from reversion.models import Revision, Version
from reversion_compare.admin import CompareVersionAdmin

from Poem.poem_super_admin.models import ExtRevision


class ProbeForm(ModelForm):
    name = CharField(help_text='Name of this probe.',
                     max_length=100,
                     widget=TextInput(attrs={'maxlength': 100,
                                             'size': 45,
                                             'readonly': 'readonly'}),
                     label='Name')
    repository = CharField(help_text='Probe repository URL',
                           max_length=100,
                           widget=TextInput(attrs={'maxlength': 100,
                                                   'size': 61,
                                                   'type': 'url',
                                                   'readonly': 'readonly'}),
                           label='Repository')
    docurl = CharField(help_text='Documentation URL',
                       max_length=100,
                       widget=TextInput(attrs={'type': 'url',
                                               'maxlength': 100,
                                               'size': 61,
                                               'readonly': 'readonly'}),
                       label='Documentation')
    comment = CharField(help_text='Short comment about this version.',
                        widget=Textarea(attrs=
                                        {'style': 'width:500px;height:100px',
                                         'readonly': True}),
                        label='Comment')
    version = CharField(help_text='Version of the probe.',
                        max_length=28,
                        widget=TextInput(attrs={'maxlength': 28,
                                                'size': 45,
                                                'readonly': 'readonly'}),
                        label='Version')
    description = CharField(help_text='Free text description outlining the '
                                      'purpose of this probe.',
                            widget=Textarea(attrs={
                                'style': 'width:500px;height:100px',
                                'readonly': True
                            }))


class ProbeAdmin(CompareVersionAdmin, admin.ModelAdmin):
    class Media:
        css = {"all": ("/poem_media/css/siteprobes.css",)}

    def num_versions(self, obj):
        num = ExtRevision.objects.filter(probeid=obj.id).count()
        return format_html(
            '<a href="{0}">{1}</a>',
            reverse('admin:poem_super_admin_probe_history',
                    args=(obj.id,)),
            num
        )
    num_versions.short_description = '# versions'

    list_display = ('name', 'num_versions', 'description')
    search_fields = ('name',)
    actions = None
    list_per_page = 20

    form = ProbeForm
    fieldsets = [
        (None, {'classes': ['infoone'], 'fields': (
            ('name', 'version',),)}),
        (None, {'classes': ['infotwo'], 'fields': (
            'repository', 'docurl', 'description', 'comment',)})
    ]

    change_list_template = ''
    object_history_template = ''
    compare_template = ''

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True

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

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        Overriding change_view to remove save button.
        """
        extra_context = extra_context or {}
        extra_context['show_save'] = False
        return super().change_view(request, object_id, form_url,
                                   extra_context=extra_context)

    def history_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}
        if request.user.is_authenticated:
            extra_context.update(dict(include_history_link=True))
        return super().history_view(request, object_id,
                                    extra_context=extra_context)
