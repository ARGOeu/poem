from django.forms import ModelForm, CharField, Textarea, ValidationError
from django.forms.widgets import TextInput, Select
from django.contrib import admin
from django.contrib import auth
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied

from Poem.poem import widgets
from Poem.poem.lookups import check_cache
from Poem.poem.admin_interface.formmodel import MyModelMultipleChoiceField
from Poem.poem.models import MetricInstance, Profile, UserProfile, VO, ServiceFlavour, GroupOfProfiles, CustUser


from ajax_select import make_ajax_field


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

class MetricInstanceFormRW(ModelForm):
    """
    Connects metric instance attributes to autocomplete widget (:py:mod:`poem.widgets`).
    """
    class Meta:
        model = MetricInstance
        exclude = ('vo',)

    metric = make_ajax_field(MetricInstance, 'metric', 'hintsmetricsall', \
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

class MetricInstanceFormRO(MetricInstanceFormRW):
    metric = CharField(label='Metric', \
                             widget=TextInput(attrs={'readonly' : 'readonly'}))
    service_flavour = CharField(label='Service Flavour', \
                                   widget=TextInput(attrs={'readonly' : 'readonly'}))

class MetricInstanceInline(admin.TabularInline):
    model = MetricInstance
    form = MetricInstanceFormRW

    def has_add_permission(self, request):
        if request.user.has_perm('poem.groupown_profile') \
                or request.user.is_superuser:
            return True
        else:
            self.form = MetricInstanceFormRO
            return False

    def has_delete_permission(self, request, obj=None):
        if request.user.has_perm('poem.groupown_profile')\
                or request.user.is_superuser:
            return True
        else:
            self.form = MetricInstanceFormRO
            return False

    def has_change_permission(self, request, obj=None):
        return True

class GroupOfProfilesInlineChangeForm(ModelForm):
    def __init__(self, *args, **kwargs):
        sh = SharedInfo()
        self.user = sh.getuser()
        self.usergroups = self.user.groupsofprofiles.all()
        super(GroupOfProfilesInlineChangeForm, self).__init__(*args, **kwargs)

    qs = GroupOfProfiles.objects.all()
    groupofprofiles = MyModelMultipleChoiceField(queryset=qs,
                                       widget=Select(),
                                       help_text='Profile is a member of given group')
    groupofprofiles.empty_label = '----------------'
    groupofprofiles.label = 'Group of profiles'

    def clean_groupofprofiles(self):
        groupsel = self.cleaned_data['groupofprofiles']
        gr = SharedInfo(grname=groupsel)
        ugid = [f.id for f in self.usergroups]
        if groupsel.id not in ugid and not self.user.is_superuser:
            raise ValidationError("You are not member of group %s." % (str(groupsel)))
        return groupsel

class GroupOfProfilesInlineAddForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(GroupOfProfilesInlineAddForm, self).__init__(*args, **kwargs)
        self.fields['groupofprofiles'].help_text = 'Select one of the groups you are member of'
        self.fields['groupofprofiles'].empty_label = None
        self.fields['groupofprofiles'].label = 'Group of profiles'

    def clean_groupofprofiles(self):
        groupsel = self.cleaned_data['groupofprofiles']
        gr = SharedInfo(grname=groupsel)
        return groupsel

class GroupOfProfilesInline(admin.TabularInline):
    model = GroupOfProfiles.profiles.through
    form = GroupOfProfilesInlineChangeForm
    verbose_name_plural = 'Group of profiles'
    verbose_name = 'Group of profile'
    max_num = 1
    extra = 1
    template = 'admin/edit_inline/stacked-group.html'


    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        if not obj:
            self.form = GroupOfProfilesInlineAddForm
        return True

    def has_change_permission(self, request, obj=None):
        if not obj:
            self.form = GroupOfProfilesInlineAddForm
        return True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        lgi = request.user.groupsofprofiles.all().values_list('id', flat=True)
        kwargs["queryset"] = GroupOfProfiles.objects.filter(pk__in=lgi)
        return super(GroupOfProfilesInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class ProfileForm(ModelForm):
    """
    Connects profile attributes to autocomplete widget (:py:mod:`poem.widgets`). Also
    adds media and does basic sanity checking for input.
    """
    class Meta:
        model = Profile

    name = CharField(help_text='Namespace and name of this profile.',
                           max_length=128,
                           widget=widgets.NamespaceTextInput(
                                           attrs={'maxlength': 128, 'size': 45}),
                           label='Profile name'
                           )
    vo = make_ajax_field(Profile, 'name', 'hintsvo', \
                         help_text='Virtual organization that owns this profile.', \
                         plugin_options = {'minLength' : 2}, label='Virtual organization')
    description = CharField(help_text='Free text description outlining the purpose of this profile.',
                                  widget=Textarea(attrs={'style':'width:480px;height:100px'}))

    def clean_vo(self):
        clean_values = []
        clean_values = check_cache('/poem/admin/lookups/ajax_lookup/hintsvo', VO, 'name')
        form_vo = self.cleaned_data['vo']
        if form_vo not in clean_values:
            raise ValidationError("Unable to find virtual organization %s." % (str(form_vo)))
        return form_vo

class ProfileAdmin(admin.ModelAdmin):
    """
    POEM admin core class that customizes its look and feel.
    """
    class Media:
        css = { "all" : ("/poem_media/css/siteprofile.css",) }

    def groupname(obj):
        return obj.groupname
    groupname.short_description = 'group'

    class GroupProfileListFilter(admin.SimpleListFilter):
        title = 'profile group'
        parameter_name = 'group'

        def lookups(self, request, model_admin):
            qs = model_admin.get_queryset(request)
            groups = set(qs.values_list('groupname', flat=True))
            return tuple((x,x) for x in filter(lambda x: x != '', groups))

        def queryset(self, request, queryset):
            if self.value():
                return queryset.filter(groupname=self.value())
            else:
                return queryset


    list_display = ('name', 'vo', 'description', groupname, )
    list_filter = ('vo', GroupProfileListFilter, )
    search_fields = ('name', 'vo',)
    fields = ('name', 'vo', 'description')
    inlines = (GroupOfProfilesInline, MetricInstanceInline, )
    exclude = ('version',)
    form = ProfileForm
    actions = None

    def _groupown_turn(self, user, flag):
        perm_prdel = Permission.objects.get(codename='delete_profile')
        try:
            perm_grpown = Permission.objects.get(codename='groupown_profile')
        except Permission.DoesNotExist:
            ct = ContentType.objects.get(app_label='poem', model='profile')
            perm_grpown = Permission.objects.create(codename='groupown_profile',
                                                   content_type=ct,
                                                   name="Group of profile owners")
        if flag == 'add':
            user.user_permissions.add(perm_grpown)
            user.user_permissions.add(perm_prdel)
        elif flag == 'del':
            user.user_permissions.remove(perm_grpown)
            user.user_permissions.remove(perm_prdel)

    def get_form(self, request, obj=None, **kwargs):
        rquser = SharedInfo(requser=request.user)
        if obj:
            ug = request.user.groupsofprofiles.all().values_list('name', flat=True)
            if obj.groupname in ug:
                self._groupown_turn(request.user, 'add')
            else:
                self._groupown_turn(request.user, 'del')
        elif not request.user.is_superuser:
            self._groupown_turn(request.user, 'add')
        return super(ProfileAdmin, self).get_form(request, obj=None, **kwargs)

    def save_model(self, request, obj, form, change):
        sh = SharedInfo()
        if obj and sh.getgroup():
            obj.groupname = sh.getgroup().name
            sh.delgroup()
        elif not obj and sh.getgroup():
            obj.groupname = sh.getgroup()
            sh.delgroup()
        if change and obj.vo:
            obj.metric_instances.update(vo=obj.vo)
        if request.user.has_perm('poem.groupown_profile') \
                or request.user.is_superuser:
            obj.save()
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
        if request.user.has_perm('poem.groupown_profile') \
                or request.user.is_superuser:
            return True
        else:
            return False

    def has_change_permission(self, request, obj=None):
        return True
