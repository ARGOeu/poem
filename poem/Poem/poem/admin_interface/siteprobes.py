from django.forms import ModelForm, CharField, Textarea
from django.forms.widgets import TextInput
from django.contrib import admin


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


class ProbeAdmin(admin.ModelAdmin):
    class Media:
        css = {"all": ("/poem_media/css/siteprobes.css",)}

    list_display = ('name', 'version', 'description')
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
