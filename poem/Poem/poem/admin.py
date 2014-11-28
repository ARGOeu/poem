"""
Admin interface is following a customization pattern explain in Django Admin docs.
The implemented hierarchy is as follows:
::
  -> class ProfileAdmin(ReadPermissionModelAdmin) uses ProfileForm & MetricInstanceInline
  \-->  class ProfileForm(forms.ModelForm)
  \-->  class MetricInstanceInline(admin.TabularInline) uses MetricInstanceForm
    \---> class MetricInstanceForm(forms.ModelForm)

Read-only ModelAdmin extension is documented in :py:mod:`poem.admin_ext`. Custom ProfileForm connects
core profile attribute to jQuery widgets. MetricInstanceForm does the same for metric instances.

"""
from django import forms
from django.forms import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.conf import settings

from piston.models import Nonce, Consumer, Token
from piston.resource import Resource

from Poem.poem.models import MetricInstance, Profile, UserProfile
from Poem.poem import widgets
from Poem.poem.admin_ext import ReadPermissionModelAdmin

HINTS_URL = u"'%s" % (settings.POEM_URL_PREFIX+"/api/0.1/json/hints")

# POEM_URL_PREFIX is needed for apache
# TODO remove it once we are done with testing
# HINTS_URL = u"'%s" % ("/api/0.1/json/hints")

class MetricInstanceForm(forms.ModelForm):
    """
    Connects metric instance attributes to autocomplete widget (:py:mod:`poem.widgets`).
    """
    class Meta:
        model = MetricInstance
        exclude = ('vo',)

    metric = forms.CharField(label='Metric', max_length=128,
                             widget = widgets.JQueryAutoComplete(
                                        options={'source': HINTS_URL+"/metrics/'",
                                                 'minLegth': 2},
                                        attrs={'maxlength': 128, 'size': 50})
                            )
    service_flavour = forms.CharField(label='Service Flavour', max_length=128,
                                widget = widgets.JQueryAutoComplete(
                                  options={'source': HINTS_URL+"/service_flavours/'",
                                           'minLength': 2},
                                  attrs={'maxlength': 128, 'size': 25})
                                )

    def clean_service_flavour(self):
        form_flavour = self.cleaned_data['service_flavour']
        return form_flavour

class MetricInstanceInline(admin.TabularInline):
    model = MetricInstance
    form = MetricInstanceForm

class ProfileForm(forms.ModelForm):
    """
    Connects profile attributes to autocomplete widget (:py:mod:`poem.widgets`). Also
    adds media and does basic sanity checking for input.
    """
    class Meta:
        model = Profile

    class Media:
        css = { "all" : ("/poem_media/css/poem_profile.custom.css",) }
        js = ( '/poem_media/js/poem-custom.js', )

    name = forms.CharField(help_text='Namespace and name of this profile.',
                           max_length=128,
                           widget = widgets.NamespaceTextInput(
                                           attrs={'maxlength': 128, 'size': 45})
                           )
    vo = forms.CharField(help_text='Virtual organization that owns this profile.',
                             label='VO', max_length=128,
                             widget = widgets.JQueryAutoComplete(
                                            options={'source': HINTS_URL+"/vo/'",
                                                     'minLength': 2},
                                            attrs={'maxlength': 128, 'size': 11})
                             )
    description = forms.CharField(help_text='Free text description outlining the purpose of this profile.',
                                  widget = forms.Textarea(attrs={'style':'width:480px;height:100px'})
                                  )
    owner = forms.CharField(required=False,
                            help_text='Certificate DN of the owner of this profile (if present it implies authorization control for changes).',
                            widget=forms.TextInput(attrs={'style':'width:540px'}))

    def clean_vo(self):
        form_vo = self.cleaned_data['vo']
        return form_vo

    def clean(self):
        # Basic object-level authorization workaround
        super(ProfileForm, self).clean()

        owner = self.instance.owner
        if self._request.user.is_superuser:
            return self.cleaned_data

        # if user has no profile (default django user) then deny
        try:
            self._request.user.get_profile()
        except UserProfile.DoesNotExist:
            raise ValidationError("Unable to authorize user, please request to add your DN to this profile (%s)." % owner)

        if owner and self._request.user.get_profile().subject != owner:
            raise ValidationError("Sorry, this profile can only be changed by its owner (%s)." % owner)

        return self.cleaned_data

class ProfileAdmin(ReadPermissionModelAdmin):
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
        return cls

    def save_model(self, request, obj, form, change):
        if change and obj.vo:
            obj.metric_instances.update(vo=obj.vo)
        obj.save()

    def get_row_css(self, obj, index):
        if not obj.valid:
            return 'row_red red%d' % index
        return ''

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
