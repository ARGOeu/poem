from Poem.poem.models import UserProfile
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.forms import ModelForm, CharField
from django.forms.widgets import TextInput


class UserProfileForm(ModelForm):
    subject = CharField(label='distinguishedName',
                        required=False,
                        widget=TextInput(attrs={'style': 'width:500px'}))
    egiid = CharField(label='eduPersonUniqueId',
                      required=False,
                      widget=TextInput(attrs={'style': 'width:500px'}))
    displayname = CharField(label='displayName',
                            required=False,
                            widget=TextInput(attrs={'style': 'width:250px'}))

    class Meta:
        fields = ['subject', 'egiid', 'displayname']


class UserProfileForm2(ModelForm):
    class Meta:
        fields = ['groupsofmetrics', 'groupsofprofiles',  'groupsofaggregations']


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    form = UserProfileForm
    can_delete = False
    verbose_name_plural = 'Additional info'
    template = 'admin/edit_inline/stacked-user.html'


class UserProfilePermissionsInline(admin.StackedInline):
    model = UserProfile
    form = UserProfileForm2
    can_delete = False
    verbose_name_plural = 'Poem user permissions'
    template = 'admin/edit_inline/stacked-user.html'

    def get_formset(self, request, obj=None, **kwargs):
        """
        Override the formset function in order to remove the add buttons in
        menus in the inline.
        """
        formset = super(UserProfilePermissionsInline, self).get_formset(
            request, obj, **kwargs
        )
        form = formset.form
        form.base_fields['groupsofmetrics'].widget.can_add_related = False
        form.base_fields['groupsofprofiles'].widget.can_add_related = False
        form.base_fields['groupsofaggregations'].widget.can_add_related = False
        return formset


class UserProfileAdmin(UserAdmin):
    view_on_site = False
    form = UserChangeForm

    class Media:
        css = {"all": ("/poem_media/css/siteuser.css",)}

    fieldsets = [(None, {'fields': ['username', 'password']}),
                 ('Personal info', {'fields': ['first_name',
                                               'last_name',
                                               'email']}),
                 ('Permissions', {'fields': ['is_superuser',
                                             'is_staff',
                                             'is_active']})]
    inlines = [UserProfilePermissionsInline, UserProfileInline]
    list_filter = ('is_superuser', 'is_staff')
    list_display = ('username', 'first_name', 'last_name',
                    'email', 'is_staff', 'is_superuser')
    filter_horizontal = ()

    def save_related(self, request, form, formsets, change):
        if formsets[0].cleaned_data == [{}] and \
                formsets[1].cleaned_data == [{}]:
            UserProfile.objects.create(user=form.instance)

        return super().save_related(request, form, formsets, change)
