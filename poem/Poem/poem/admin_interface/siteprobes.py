from django.forms import ModelForm, CharField, Textarea
from django.forms.widgets import TextInput, Select
from django.contrib import admin
from django.contrib import auth
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied

from Poem.poem import widgets
from Poem.poem.lookups import check_cache
from Poem.poem.admin_interface.formmodel import MyModelMultipleChoiceField
from Poem.poem.models import MetricInstance, Probe, UserProfile, VO, ServiceFlavour, GroupOfProbes, CustUser

from ajax_select import make_ajax_field


class SharedInfo:
    def __init__(self, requser=None):
        if requser:
            self.__class__.user = requser

    def getuser(self):
        if getattr(self.__class__, 'user', None):
            return self.__class__.user
        else:
            return None

class MetricInstanceForm(ModelForm):
    """
    Connects metric instance attributes to autocomplete widget (:py:mod:`poem.widgets`).
    """
    class Meta:
        model = MetricInstance
        exclude = ('vo',)

    metric = make_ajax_field(MetricInstance, 'metric', 'hintsmetrics', \
                             plugin_options = {'minLength' : 2})
    service_flavour = make_ajax_field(ServiceFlavour, 'name', 'hintsserviceflavours', \
                                      plugin_options = {'minLength' : 2})

    def clean_service_flavour(self):
        clean_values = []
        clean_values = check_cache('/poem/admin/lookups/ajax_lookup/hintsserviceflavours', \
                                   ServiceFlavour, 'name')
        form_flavour = self.cleaned_data['service_flavour']
        if form_flavour not in clean_values:
            raise ValidationError("Unable to find flavour %s." % (str(form_flavour)))
        return form_flavour

class MetricInstanceFormRO(MetricInstanceForm):
    metric = CharField(label='Metric', \
                             widget=TextInput(attrs={'readonly' : 'readonly'}))
    service_flavour = CharField(label='Service Flavour', \
                                   widget=TextInput(attrs={'readonly' : 'readonly'}))

class MetricInstanceInline(admin.TabularInline):
    model = MetricInstance
    form = MetricInstanceForm

    def has_add_permission(self, request):
        if request.user.has_perm('poem.groupown_profile'):
            return True
        if request.user.has_perm('poem.readonly_profile') and \
                not request.user.is_superuser:
            self.form = MetricInstanceFormRO
            return False
        else:
            return True

    def has_delete_permission(self, request, obj=None):
        if request.user.has_perm('poem.groupown_profile'):
            return True
        if request.user.has_perm('poem.readonly_profile') and \
                not request.user.is_superuser:
            self.form = MetricInstanceFormRO
            return False
        else:
            return True

    def has_change_permission(self, request, obj=None):
        return True

class GroupOfProbesInlineForm(ModelForm):
    def __init__(self, *args, **kwargs):
        rquser = SharedInfo()
        self.user = rquser.getuser()
        self.usergroups = self.user.groupsofprofiles.all()
        super(GroupOfProbesInlineForm, self).__init__(*args, **kwargs)


    qs = GroupOfProbes.objects.all()
    groupofprobes = MyModelMultipleChoiceField(queryset=qs,
                                       widget=Select(),
                                       help_text='Probe is a member of given group')
    groupofprobes.empty_label = '----------------'
    groupofprobes.label = 'Group of probes'

    def clean_group(self):
        groupsel = self.cleaned_data['groupofprobes']
        ugid = [f.id for f in self.usergroups]
        if groupsel.id not in ugid and not self.user.is_superuser:
            raise ValidationError("You are not member of group %s." % (str(groupsel)))
        return groupsel

class GroupOfProbesInlineAdd(ModelForm):
    def __init__(self, *args, **kwargs):
        super(GroupOfProbesInlineAdd, self).__init__(*args, **kwargs)
        self.fields['group'].help_text = 'Select one of the groups you are member of'
        self.fields['group'].empty_label = None

class GroupOfProbesInline(admin.TabularInline):
    model = GroupOfProbes.probes.through
    form = GroupOfProbesInlineForm
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

class GroupOfProbesInlineAdd(GroupOfProbesInline):
    form = GroupOfProbesInlineAdd

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        lgi = request.user.groupofprobes.all().values_list('id', flat=True)
        kwargs["queryset"] = GroupOfProbes.objects.filter(pk__in=lgi)
        return super(GroupOfProbesInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

class ProbeForm(ModelForm):
    """
    Connects profile attributes to autocomplete widget (:py:mod:`poem.widgets`). Also
    adds media and does basic sanity checking for input.
    """
    class Meta:
        model = Probe

    name = CharField(help_text='Name of this probe.',
                     max_length=128,
                     widget=TextInput(attrs={'maxlength': 128, 'size': 45}),
                     label='Probe name')
    version = CharField(help_text='Version of the probe.',
                        max_length=128,
                        widget=TextInput(attrs={'maxlength': 128, 'size': 45}),
                        label='Probe version')
    description = CharField(help_text='Free text description outlining the purpose of this probe.',
                            widget=Textarea(attrs={'style':'width:480px;height:100px'}))

class ProbeAdmin(admin.ModelAdmin):
    """
    POEM admin core class that customizes its look and feel.
    """
    class Media:
        css = { "all" : ("/poem_media/css/poem_profile.custom.css",) }

    list_display = ('name', 'description')
    search_fields = ('name',)
    fields = ('name', 'version', 'description')
    inlines = (GroupOfProbesInline, )
    form = ProbeForm
    actions = None

    def _groupown_turn(self, user, flag):
        perm_prdel = Permission.objects.get(codename='delete_probes')
        try:
            perm_grpown = Permission.objects.get(codename='groupown_probes')
        except Permission.DoesNotExist:
            ct = ContentType.objects.get(app_label='poem', model='probes')
            perm_grpown = Permission.objects.create(codename='groupown_probes',
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
                gp = GroupOfProbes.objects.get(probes__id=obj.id)
                ugis = request.user.groupsofprobes.all().values_list('id', flat=True)
                if ugis:
                    for ugi in ugis:
                        if ugi == gp.id:
                            self._groupown_turn(request.user, 'add')
                            break
                        else:
                            self._groupown_turn(request.user, 'del')
            except GroupOfProbes.DoesNotExist:
                self._groupown_turn(request.user, 'del')
        elif not request.user.is_superuser:
            self.inlines = (GroupOfProbesInlineAdd, )
            self._groupown_turn(request.user, 'add')
        return super(ProbeAdmin, self).get_form(request, obj=None, **kwargs)

    def save_model(self, request, obj, form, change):
        if change and obj.vo:
            obj.metric_instances.update(vo=obj.vo)
        if request.user.has_perm('poem.groupown_probes'):
            obj.save()
            return
        if not request.user.has_perm('poem.readonly_probes') or \
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
        if request.user.groupsofprofiles.count():
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        if request.user.has_perm('poem.groupown_probes'):
            return True
        if request.user.has_perm('poem.readonly_probe') and \
                not request.user.is_superuser:
            return False
        else:
            return True

    def has_change_permission(self, request, obj=None):
        return True
