from itertools import chain
from django import forms
from django.forms import ValidationError, models
from django.contrib.auth.models import User, Permission
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.http import HttpResponseRedirect, HttpResponse
from django.core import exceptions, validators
from django.contrib import admin
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.utils.encoding import force_unicode
from django.utils.html import escape
from django.forms.util import flatatt
from django.utils.safestring import mark_safe
from django.contrib.admin.templatetags.admin_static import static

from Poem import poem
from django.contrib import auth

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
    class Media:
        css = { "all" : ("/poem_media/css/poem_profile.custom.css",) }

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

class UserProfileForm(forms.ModelForm):
    subject = forms.CharField(widget=forms.TextInput(attrs={'style':'width:500px'}))

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    form = UserProfileForm
    can_delete = False
    verbose_name_plural = 'Additional info'

class UserProfileAdmin(UserAdmin):
    class Media:
        css = { "all" : ("/poem_media/css/poem_profile.custom.css",) }

    fieldsets = [(None, {'fields': ['username', 'password']}),
                 ('Personal info', {'fields': ['first_name', 'last_name', 'email']}),
                 ('Permissions', {'fields': ['is_superuser', 'groups']})]
    inlines = [UserProfileInline]


admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)

class MyModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, queryset, cache_choices=False, required=True, widget=None, label=None,
                 initial=None, help_text=None, ftype='', *args, **kwargs):
        self.ftype = ftype
        super(forms.ModelMultipleChoiceField, self).__init__(queryset, None, cache_choices, required, widget,
                                                       label, initial, help_text, *args, **kwargs)
    def clean(self, value):
        if self.required and not value:
            raise ValidationError(self.error_messages['required'])
        elif not self.required and not value:
            return []
        if not isinstance(value, (list, tuple)):
            raise ValidationError(self.error_messages['list'])
        key = self.to_field_name or 'pk'
        for pk in value:
            try:
                self.queryset.filter(**{key: pk})
            except ValueError:
                raise ValidationError(self.error_messages['invalid_pk_value'] % pk)
        if self.ftype == 'profiles':
            qs = Profile.objects.filter(**{'%s__in' % key: value})
        else:
            qs = self.queryset.filter(**{'%s__in' % key: value})
        pks = set([force_unicode(getattr(o, key)) for o in qs])
        for val in value:
            if force_unicode(val) not in pks:
                raise ValidationError(self.error_messages['invalid_choice'] % val)
        if self.ftype != 'profiles':
            self.run_validators(value)
        return qs

    def run_validators(self, value):
        if value in validators.EMPTY_VALUES:
            return

        errors = []
        for v in self.validators:
            try:
                v(value)
            except exceptions.ValidationError, e:
                if hasattr(e, 'code') and e.code in self.error_messages:
                    message = self.error_messages[e.code]
                    if e.params:
                        message = message % e.params
                    errors.append(message)
                else:
                    errors.extend(e.messages)
        if errors:
            raise exceptions.ValidationError(errors)

    def label_from_instance(self, obj):
        return str(obj.name)

class MySelectMultiple(forms.widgets.SelectMultiple):
    allow_multiple_selected = False

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<select%s>' % flatatt(final_attrs)]
        options = self.render_options(choices, [value])
        if options:
            output.append(options)
        output.append(u'</select>')
        return mark_safe(u'\n'.join(output))

class MyFilteredSelectMultiple(admin.widgets.FilteredSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        self.selformname = name
        if attrs is None:
            attrs = {}
        attrs['class'] = 'selectfilter'
        if self.is_stacked:
            attrs['class'] += 'stacked'
        output = [super(MyFilteredSelectMultiple, self).render(name, value, attrs, choices)]
        output.append(u'<script type="text/javascript">addEvent(window, "load", function(e) {')
        output.append(u'SelectFilter.init("id_%s", "%s", %s, "%s"); });</script>\n'
            % (name, self.verbose_name.replace('"', '\\"'), int(self.is_stacked), static('admin/')))
        return mark_safe(u''.join(output))

    def render_options(self, choices, selected_choices):
        selected_choices = set(force_unicode(v) for v in selected_choices)
        output = []
        if self.selformname == 'profiles':
            for sel in selected_choices:
                output.append('<option value="%s" selected="selected">' % (sel)
                              + str(Profile.objects.get(id=int(sel)))
                              + '</option>\n')
        for option_value, option_label in chain(self.choices, choices):
            if isinstance(option_label, (list, tuple)):
                output.append(u'<optgroup label="%s">' % escape(force_unicode(option_value)))
                for option in option_label:
                    output.append(self.render_option(selected_choices, *option))
                output.append(u'</optgroup>')
            else:
                output.append(self.render_option(selected_choices, option_value, option_label))
        return u'\n'.join(output)

class GroupPermForm(forms.ModelForm):
    class Meta:
        model = poem.models.Group
    queryset = Permission.objects.filter(codename__startswith='cust')
    permissions = MyModelMultipleChoiceField(queryset=queryset, widget=MySelectMultiple)
    queryset = Profile.objects.filter(group__id__isnull=True)
    profiles = MyModelMultipleChoiceField(queryset=queryset, widget=MyFilteredSelectMultiple('Profiles', False), ftype='profiles')

class CustGroupAdmin(GroupAdmin):
    class Media:
        css = { "all" : ("/poem_media/css/poem_profile.custom.css",) }

    form = GroupPermForm
    search_field = ()
    filter_horizontal=('profiles',)
    fieldsets = [(None, {'fields': ['name']}),
                 ('Permissions', {'fields': ['permissions', 'profiles']})]

admin.site.unregister(auth.models.Group)
admin.site.register(poem.models.Group, CustGroupAdmin)
