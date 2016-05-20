from django.db import transaction
from django.forms import ModelForm, CharField, Textarea, ValidationError
from django.forms.widgets import TextInput, Select
from django.contrib import admin
from django.contrib import auth
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.utils.html import format_html

from Poem.poem import widgets
from Poem.poem.lookups import check_cache
from Poem.poem.admin_interface.formmodel import MyModelMultipleChoiceField
from Poem.poem.models import MetricInstance, Probe, UserProfile, VO, ServiceFlavour, GroupOfProbes, CustUser, ExtRevision

from ajax_select import make_ajax_field
from reversion_compare.admin import CompareVersionAdmin
import reversion

class SharedInfo:
    def __init__(self, requser=None, grname=None):
        if requser:
            self.__class__.user = requser
        if grname:
            self.__class__.group = grname

    def getgroup(self):
        if getattr(self.__class__, 'group', None):
            return self.__class__.group
        else:
            return None

    def delgroup(self):
        self.__class__.group = None


    def getuser(self):
        if getattr(self.__class__, 'user', None):
            return self.__class__.user
        else:
            return None

class GroupOfProbesInlineChangeForm(ModelForm):
    def __init__(self, *args, **kwargs):
        rquser = SharedInfo()
        self.user = rquser.getuser()
        self.usergroups = self.user.groupsofprobes.all()
        super(GroupOfProbesInlineChangeForm, self).__init__(*args, **kwargs)

    qs = GroupOfProbes.objects.all()
    groupofprobes = MyModelMultipleChoiceField(queryset=qs,
                                       widget=Select(),
                                       help_text='Probe is a member of given group')
    groupofprobes.empty_label = '----------------'
    groupofprobes.label = 'Group'

    def clean_groupofprobes(self):
        groupsel = self.cleaned_data['groupofprobes']
        gr = SharedInfo(grname=groupsel)
        ugid = [f.id for f in self.usergroups]
        if groupsel.id not in ugid and not self.user.is_superuser:
            raise ValidationError("You are not member of group %s." % (str(groupsel)))
        return groupsel

class GroupOfProbesInlineAddForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(GroupOfProbesInlineAddForm, self).__init__(*args, **kwargs)
        self.fields['groupofprobes'].help_text = 'Select one of the groups you are member of'
        self.fields['groupofprobes'].empty_label = None
        self.fields['groupofprobes'].label = 'Group'
        self.fields['groupofprobes'].widget.can_add_related = False

    def clean_groupofprobes(self):
        groupsel = self.cleaned_data['groupofprobes']
        gr = SharedInfo(grname=groupsel)
        return groupsel

class GroupOfProbesInline(admin.TabularInline):
    model = GroupOfProbes.probes.through
    form = GroupOfProbesInlineChangeForm
    verbose_name_plural = 'Group of probes'
    verbose_name = 'Group of probes'
    max_num = 1
    extra = 1
    template = 'admin/edit_inline/stacked-group.html'

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        if not obj:
            self.form = GroupOfProbesInlineAddForm
        return True

    def has_change_permission(self, request, obj=None):
        if not obj:
            self.form = GroupOfProbesInlineAddForm
        return True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            lgi = request.user.groupsofprobes.all().values_list('id', flat=True)
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
                     max_length=100,
                     widget=TextInput(attrs={'maxlength': 100, 'size': 45}),
                     label='Name')
    docurl = CharField(help_text='Documentation URL',
                     max_length=100,
                     widget=TextInput(attrs={'maxlength': 100, 'size': 45}),
                     label='Documentation')
    comment = CharField(help_text='Short comment about this version.',
                     widget=Textarea(attrs={'style':'width:480px;height:100px'}),
                     label='Comment')
    version = CharField(help_text='Version of the probe.',
                        max_length=28,
                        widget=TextInput(attrs={'maxlength': 28, 'size': 45}),
                        label='Version')
    description = CharField(help_text='Free text description outlining the purpose of this probe.',
                            widget=Textarea(attrs={'style':'width:480px;height:100px'}))

    user = CharField(help_text='User that added the probe', max_length=64, required=False)
    datetime = CharField(help_text='Time when probe is added', max_length=64, required=False)

class ProbeAdmin(CompareVersionAdmin, admin.ModelAdmin):
    """
    POEM admin core class that customizes its look and feel.
    """
    class Media:
        css = { "all" : ("/poem_media/css/siteprobes.css",) }

    def groupname(obj):
        return obj.group
    groupname.short_description = 'Group'

    class GroupProbesListFilter(admin.SimpleListFilter):
        title = 'probes group'
        parameter_name = 'group'

        def lookups(self, request, model_admin):
            qs = model_admin.get_queryset(request)
            groups = set(qs.values_list('group', flat=True))
            return tuple((x,x) for x in filter(lambda x: x != '', groups))

        def queryset(self, request, queryset):
            if self.value():
                return queryset.filter(group=self.value())
            else:
                return queryset

    def num_versions(self, obj):
        num = ExtRevision.objects.filter(probeid=obj.id).count()
        return format_html('<a href="{0}">{1}</a>', reverse('admin:poem_probe_history', args=(obj.id,)), num)
    num_versions.short_description = '# versions'


    list_display = ('name', 'num_versions', 'description', groupname)
    list_filter= (GroupProbesListFilter, )
    search_fields = ('name',)
    inlines = (GroupOfProbesInline, )
    form = ProbeForm
    actions = None

    change_list_template = ''
    object_history_template = ''
    compare_template = ''

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
        rquser = SharedInfo(requser=request.user)
        if not request.user.is_superuser:
            ug = request.user.groupsofprobes.all().values_list('name', flat=True)
            if obj.group in ug:
                self._groupown_turn(request.user, 'add')
            else:
                self._groupown_turn(request.user, 'del')
        if obj:
            self.fieldsets = ((None, {'classes': ['infoone'], 'fields': (('name', 'version',), 'datetime', 'user', )}),
                              (None, {'classes': ['infotwo'], 'fields': ('docurl', 'description','comment',)}),)
            self.readonly_fields = ('user', 'datetime',)
        else:
            self.fieldsets = ((None, {'classes': ['infoone'], 'fields': (('name', 'version',),)}),
                              (None, {'classes': ['infotwo'], 'fields': ('docurl', 'description','comment', )}),)
            self.readonly_fields = ()
        return super(ProbeAdmin, self).get_form(request, obj=None, **kwargs)

    def save_model(self, request, obj, form, change):
        sh = SharedInfo()

        if obj and sh.getgroup():
            obj.group = sh.getgroup().name
            sh.delgroup()
        elif not obj and sh.getgroup():
            obj.group = sh.getgroup()
            sh.delgroup()
        if request.user.has_perm('poem.groupown_probe') \
                or request.user.is_superuser:
            obj.user = request.user.username
            obj.save()
            return
        else:
            raise PermissionDenied()

    def get_row_css(self, obj, index):
        if not obj.valid:
            return 'row_red red%d' % index
        return ''

    def has_add_permission(self, request):
        if request.user.is_superuser and GroupOfProbes.objects.count():
            return True
        if request.user.groupsofprobes.count():
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        if request.user.has_perm('poem.groupown_probe') \
                or request.user.is_superuser:
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        return True

    def revision_view(self, request, object_id, version_id, extra_context=None):
        currev = reversion.models.Version.objects.get(pk=version_id).object_repr
        if extra_context:
            extra_context.update({'cursel': currev})
        else:
            extra_context = {'cursel': currev}
        return super(ProbeAdmin, self).revision_view(request, object_id, version_id, extra_context)

reversion.register(Probe, exclude=["nameversion", "datetime"])
