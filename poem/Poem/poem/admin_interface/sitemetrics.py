from django.forms import ModelForm, CharField, Textarea, ModelChoiceField
from django.forms.widgets import TextInput, Select
from django.contrib import admin
from django.contrib import auth
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext as _

from Poem.poem import widgets
from Poem.poem.lookups import check_cache
from Poem.poem.admin_interface.formmodel import MyModelMultipleChoiceField, MyModelChoiceField, MySelect
from Poem.poem.models import MetricsProbe, Probe, UserProfile, VO, ServiceFlavour, GroupOfProbes, CustUser, Tags, Metrics, GroupOfMetrics

from ajax_select import make_ajax_field


class MetricsProbeAddForm(ModelForm):
    """
    Connects profile attributes to autocomplete widget (:py:mod:`poem.widgets`). Also
    adds media and does basic sanity checking for input.
    """
    def __init__(self, *args, **kwargs):
        super(MetricsProbeAddForm, self).__init__(*args, **kwargs)
        self.fields['group'].widget.can_add_related = False
        self.fields['group'].empty_label = None

    class Meta:
        model = MetricsProbe
        labels = {
            'group': _('Group of metrics'),
        }
        help_texts = {
            'group': _('(Metric, Probe Version) is member of given group'),
        }

    qs = Tags.objects.all()
    tag = MyModelChoiceField(queryset=qs, label='Tags', help_text='Select one of the tags available.')
    tag.empty_label = None
    name = make_ajax_field(Metrics, 'name', 'hintsmetrics',
                           plugin_options={'minLength': 2}, label='Metrics', help_text='Metric name')
    probever = make_ajax_field(Probe, 'nameversion', 'hintsprobes', label='Probes')
    config = CharField(help_text='List of key, value pairs that configure the metric.',
                       max_length=100,
                       widget=Textarea(attrs={'style':'width:480px;height:100px'}))
    docurl = CharField(help_text='Location of metric documentation.',
                       max_length=128,
                       widget=TextInput(attrs={'maxlenght': 128, 'size': 45}),
                       label='Documentation URL')

    def clean_tag(self):
        fetched = self.cleaned_data['tag']
        return Tags.objects.get(id=fetched.id)

    def clean_probever(self):
        fetched = self.cleaned_data['probever']
        return Probe.objects.get(nameversion__exact=fetched)

class MetricsProbeChangeRWForm(MetricsProbeAddForm):
    pass

class MetricsProbeChangeROForm(MetricsProbeAddForm):
    pass

class MetricsProbeAdmin(admin.ModelAdmin):
    """
    POEM admin core class that customizes its look and feel.
    """
    class Media:
        css = { "all" : ("/poem_media/css/sitemetrics.css",) }


    list_display = ('name', 'tag', 'probever', 'docurl', 'config', 'group')
    fields = ('name', 'tag', 'probever', 'docurl', 'config', 'group')
    list_filter = ('tag', 'group__name', )
    search_fields = ('name',)
    actions = None
    ordering = ('name',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'group' and not request.user.is_superuser:
            lgi = request.user.groupsofmetrics.all().values_list('id', flat=True)
            kwargs["queryset"] = GroupOfMetrics.objects.filter(pk__in=lgi)
        return super(MetricsProbeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def _groupown_turn(self, user, flag):
        perm_prdel = Permission.objects.get(codename='delete_metrics')
        try:
            perm_grpown = Permission.objects.get(codename='groupown_metrics')
        except Permission.DoesNotExist:
            ct = ContentType.objects.get(app_label='poem', model='metrics')
            perm_grpown = Permission.objects.create(codename='groupown_metrics',
                                                   content_type=ct,
                                                   name="Group of metric owners")
        if flag == 'add':
            user.user_permissions.add(perm_grpown)
            user.user_permissions.add(perm_prdel)
        elif flag == 'del':
            user.user_permissions.remove(perm_grpown)
            user.user_permissions.remove(perm_prdel)

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            # TODO: fetch all see prefetch_related()
            if request.user.is_superuser:
                self.form = MetricsProbeChangeRWForm
                self._groupown_turn(request.user, 'add')
            else:
                ug = request.user.groupsofmetrics.all()
                if ug and obj.group not in ug:
                    self.form = MetricsProbeChangeROForm
                    self._groupown_turn(request.user, 'del')
                elif not ug:
                    self.form = MetricsProbeChangeROForm
                    self._groupown_turn(request.user, 'del')
                else:
                    self.form = MetricsProbeChangeRWForm
                    self._groupown_turn(request.user, 'add')
        else:
            self.form = MetricsProbeAddForm
            if request.user.is_superuser or request.user.groupsofmetrics.count():
                self._groupown_turn(request.user, 'add')
            else:
                self._groupown_turn(request.user, 'del')
        return super(MetricsProbeAdmin, self).get_form(request, obj=None, **kwargs)

    def save_model(self, request, obj, form, change):
        if request.user.has_perm('poem.groupown_probe'):
            obj.save()
            return
        if not request.user.has_perm('poem.readonly_probe') or \
                request.user.is_superuser:
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
        if request.user.groupsofmetrics.count():
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        if request.user.has_perm('poem.groupown_probe'):
            return True
        if request.user.has_perm('poem.readonly_probe') and \
                not request.user.is_superuser:
            return False
        else:
            return True

    def has_change_permission(self, request, obj=None):
        return True
