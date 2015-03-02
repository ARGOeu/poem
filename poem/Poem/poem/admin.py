from django import forms
from django.forms import ValidationError
from django.contrib.auth.models import User, Permission
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import PermissionDenied

from Poem.poem.models import MetricInstance, Profile, UserProfile, VO, ServiceFlavour
from Poem.poem import widgets
from Poem.poem.lookups import check_cache
from ajax_select import make_ajax_field


dnowner = ""

class MetricInstanceForm(forms.ModelForm):
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
    metric = forms.CharField(label='Metric', \
                             widget=forms.TextInput(attrs={'readonly' : 'readonly'}))
    service_flavour = forms.CharField(label='Service Flavour', \
                                   widget=forms.TextInput(attrs={'readonly' : 'readonly'}))

class MetricInstanceInline(admin.TabularInline):
    model = MetricInstance
    form = MetricInstanceForm

    def has_add_permission(self, request):
        try:
            if request.META['SSL_CLIENT_S_DN'] == dnowner:
                return True
        except KeyError:
            pass
        if request.user.has_perm('poem.readonly_profile') and \
                not request.user.is_superuser:
            self.form = MetricInstanceFormRO
            return False
        else:
            return True

    def has_delete_permission(self, request, obj=None):
        try:
            if request.META['SSL_CLIENT_S_DN'] == dnowner:
                return True
        except KeyError:
            pass
        if request.user.has_perm('poem.readonly_profile') and \
                not request.user.is_superuser:
            self.form = MetricInstanceFormRO
            return False
        else:
            return True

    def has_change_permission(self, request, obj=None):
        # if request.user.has_perm('poem.readonly_profile'):
        #     self.readonly_fields = ('profile', 'service_flavour', 'metric', 'fqan')
        return True

class ProfileForm(forms.ModelForm):
    """
    Connects profile attributes to autocomplete widget (:py:mod:`poem.widgets`). Also
    adds media and does basic sanity checking for input.
    """
    class Meta:
        model = Profile

    class Media:
        css = { "all" : ("/poem_media/css/poem_profile.custom.css",) }

    name = forms.CharField(help_text='Namespace and name of this profile.',
                           max_length=128,
                           widget = widgets.NamespaceTextInput(
                                           attrs={'maxlength': 128, 'size': 45})
                           )
    vo = make_ajax_field(Profile, 'name', 'hintsvo', \
                         help_text='Virtual organization that owns this profile.', \
                         plugin_options = {'minLength' : 2})
    description = forms.CharField(help_text='Free text description outlining the purpose of this profile.', widget=forms.Textarea(attrs={'style':'width:480px;height:100px'}))
    owner = forms.CharField(required=False, help_text='Certificate DN of the owner of this profile (if present it implies authorization control for changes).', widget=forms.TextInput(attrs={'style':'width:540px'}))

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
    list_display = ('name', 'vo', 'description')
    list_filter = ('vo',)
    search_fields = ('name', 'vo',)
    fields = ('name', 'vo', 'owner', 'description')
    inlines = (MetricInstanceInline,)
    exclude = ('version',)
    form = ProfileForm

    def get_form(self, request, obj=None, **kwargs):
        cls = super(ProfileAdmin, self).get_form(request, obj=None, **kwargs)
        cls._request = request
        global dnowner
        dnowner = obj.owner if obj else None
        return cls

    def save_model(self, request, obj, form, change):
        if change and obj.vo:
            obj.metric_instances.update(vo=obj.vo)
        try:
            if request.META['SSL_CLIENT_S_DN'] == dnowner:
                obj.save()
                return
        except KeyError:
            pass
        if not request.user.has_perm('poem.readonly_profile') or \
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
        try:
            if request.META['SSL_CLIENT_S_DN'] == dnowner:
                ownerperm = Permission.objects.get(codename='owner')
                request.user.user_permissions.add(ownerperm)
                return True
            elif request.user.has_perm('poem.owner'):
                ownerperm = Permission.objects.get(codename='owner')
                request.user.user_permissions.remove(ownerperm)
        except KeyError:
            pass
        if request.user.has_perm('poem.readonly_profile') and \
                not request.user.is_superuser:
            return False
        else:
            return True

    def has_delete_permission(self, request, obj=None):
        try:
            if request.META['SSL_CLIENT_S_DN'] == dnowner:
                ownerperm = Permission.objects.get(codename='owner')
                request.user.user_permissions.add(ownerperm)
                return True
            elif request.user.has_perm('poem.owner'):
                ownerperm = Permission.objects.get(codename='owner')
                request.user.user_permissions.remove(ownerperm)
        except KeyError:
            pass
        if request.user.has_perm('poem.readonly_profile') and \
                not request.user.is_superuser:
            return False
        else:
            return True

    def has_change_permission(self, request, obj=None):
        return True


admin.site.register(Profile, ProfileAdmin)

admin.site.unregister(User)

class UserProfileForm(forms.ModelForm):
    subject = forms.CharField(widget=forms.TextInput(attrs={'style':'width:500px'}))

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    form = UserProfileForm

class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline]

admin.site.register(User, UserProfileAdmin)
