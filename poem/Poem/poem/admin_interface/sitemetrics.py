from django.forms import ModelForm, CharField, Textarea, ModelChoiceField
from django.forms.widgets import TextInput, Select
from django.contrib import admin
from django.contrib import auth
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied

from Poem.poem import widgets
from Poem.poem.lookups import check_cache
from Poem.poem.admin_interface.formmodel import MyModelMultipleChoiceField, MyModelChoiceField
from Poem.poem.models import MetricsProbe, Probe, UserProfile, VO, ServiceFlavour, GroupOfProbes, CustUser, Tags, Metrics, GroupOfMetrics


from ajax_select import make_ajax_field
from ajax_select.fields import AutoCompleteField, AutoCompleteSelectField, AutoCompleteSelectMultipleField

class SharedInfo:
    def __init__(self, requser=None):
        if requser:
            self.__class__.user = requser

    def getuser(self):
        if getattr(self.__class__, 'user', None):
            return self.__class__.user
        else:
            return None

class GroupOfMetricsInlineForm(ModelForm):
    def __init__(self, *args, **kwargs):
        rquser = SharedInfo()
        self.user = rquser.getuser()
        self.usergroups = self.user.groupsofprofiles.all()
        super(GroupOfMetricsInlineForm, self).__init__(*args, **kwargs)


    qs = GroupOfProbes.objects.all()
    groupofprobes = MyModelMultipleChoiceField(queryset=qs,
                                       widget=Select(),
                                       help_text='Probe is a member of given group')
    groupofprobes.empty_label = '----------------'
    groupofprobes.label = 'Group of probes'

    def clean_groupofprobes(self):
        groupsel = self.cleaned_data['groupofprobes']
        ugid = [f.id for f in self.usergroups]
        if groupsel.id not in ugid and not self.user.is_superuser:
            raise ValidationError("You are not member of group %s." % (str(groupsel)))
        return groupsel

class GroupOfMetricsInlineAdd(ModelForm):
    def __init__(self, *args, **kwargs):
        super(GroupOfMetricsInlineAdd, self).__init__(*args, **kwargs)
        self.fields['group'].help_text = 'Select one of the groups you are member of'
        self.fields['group'].empty_label = None

class GroupOfMetricsInline(admin.TabularInline):
    model = GroupOfProbes.probes.through
    form = GroupOfMetricsInlineForm
    verbose_name_plural = 'Group of probes'
    verbose_name = 'Group of probes'
    max_num = 1
    extra = 1
    template = 'admin/edit_inline/stacked-group.html'

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True

class GroupOfMetricsInlineAdd(GroupOfMetricsInline):
    form = GroupOfMetricsInlineAdd

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        lgi = request.user.groupofprobes.all().values_list('id', flat=True)
        kwargs["queryset"] = GroupOfProbes.objects.filter(pk__in=lgi)
        return super(GroupOfMetricsInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

class MetricsProbeForm(ModelForm):
    """
    Connects profile attributes to autocomplete widget (:py:mod:`poem.widgets`). Also
    adds media and does basic sanity checking for input.
    """
    class Meta:
        model = MetricsProbe

    # tag = make_ajax_field(Tags, 'name', 'hintstags', label='Tags')
    tag = MyModelChoiceField(queryset=Tags.objects, cache_choices=True,
                           initial='Test', label='Tags', help_text='Select one of the tags available.')
    name = make_ajax_field(Metrics, 'name', 'hintsmetrics',
                           plugin_options={'minLength': 2}, label='Metrics', help_text='Metric name')
    probever = AutoCompleteField('hintsprobes', label='Probes')
    config = CharField(help_text='List of key, value pairs that configure the metric.',
                       max_length=100,
                       widget=Textarea(attrs={'style':'width:480px;height:100px'}))
    docurl = CharField(help_text='Location of metric documentation.',
                       max_length=128,
                       widget=TextInput(attrs={'maxlenght': 128, 'size': 45}),
                       label='Documentation URL')
    group = CharField(help_text='Group that metric belong to.', label='Metric group',
                     widget=TextInput(attrs={'readonly': 'readonly'}))

    def clean_tag(self):
        fetched = self.cleaned_data['tag']
        return Tags.objects.get(id=fetched.id).name

    def clean_probever(self):
        fetched = self.cleaned_data['probever']
        return Probe.objects.get(nameversion__exact=fetched)

class MetricsProbeAdmin(admin.ModelAdmin):
    """
    POEM admin core class that customizes its look and feel.
    """
    class Media:
        css = { "all" : ("/poem_media/css/sitemetrics.css",) }

    def groupbelong(obj):
        if obj.groupofmetrics_set.count():
            return obj.groupofmetrics_set.values('name')[0]['name']
        else:
            return ''
    groupbelong.short_description = 'Group'


    list_display = ('name', 'tag', 'probever', 'docurl', 'config', 'group')
    fields = ('name', 'tag', 'probever', 'docurl', 'config', 'group')
    list_filter = ('tag', 'group')
    search_fields = ('name',)
    # fields = ('name', )
    # inlines = (GroupOfProbes, )
    form = MetricsProbeForm
    actions = None
    ordering = ('name',)

    def _groupown_turn(self, user, flag):
        perm_prdel = Permission.objects.get(codename='delete_probe')
        try:
            perm_grpown = Permission.objects.get(codename='groupown_probe')
        except Permission.DoesNotExist:
            ct = ContentType.objects.get(app_label='poem', model='probe')
            perm_grpown = Permission.objects.create(codename='groupown_probe',
                                                   content_type=ct,
                                                   name="Group of probe owners")
        if flag == 'add':
            user.user_permissions.add(perm_grpown)
            user.user_permissions.add(perm_prdel)
        elif flag == 'del':
            user.user_permissions.remove(perm_grpown)
            user.user_permissions.remove(perm_prdel)

    def get_form(self, request, obj=None, **kwargs):
        rquser = SharedInfo(request.user)
        if obj:
            try:
                gp = GroupOfMetrics.objects.get(metrics__id=obj.id)
                ugis = request.user.groupsofmetrics.all().values_list('id', flat=True)
                if ugis:
                    for ugi in ugis:
                        if ugi == gp.id:
                            self._groupown_turn(request.user, 'add')
                            break
                        else:
                            self._groupown_turn(request.user, 'del')
            except GroupOfMetrics.DoesNotExist:
                self._groupown_turn(request.user, 'del')
        elif not request.user.is_superuser:
            self.inlines = (GroupOfMetricsInlineAdd, )
            self._groupown_turn(request.user, 'add')
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
