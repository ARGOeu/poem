from Poem.poem.models import UserProfile, CustUser
from django.contrib import admin
from django.contrib import auth
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.admin import UserAdmin
from Poem.poem.admin_interface.formmodel import MyUserCreationForm, MyUserChangeForm
from django.forms import ModelForm, CharField
from django.forms.widgets import TextInput

class UserProfileForm(ModelForm):
    subject = CharField(widget=TextInput(attrs={'style':'width:500px'}))

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    form = UserProfileForm
    can_delete = False
    verbose_name_plural = 'Additional info'

class UserProfileAdmin(UserAdmin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm

    class Media:
        css = { "all" : ("/poem_media/css/siteuser.css",) }

    fieldsets = [(None, {'fields': ['username', 'password']}),
                 ('Personal info', {'fields': ['first_name', 'last_name', 'email']}),
                 ('Permissions', {'fields': ['is_superuser', 'is_staff', 'is_active', 'groupsofprofiles', 'groupsofmetrics', 'groupsofprobes']})]
    inlines = [UserProfileInline]
    list_filter = ('is_superuser',)
    filter_horizontal = ('user_permissions',)
