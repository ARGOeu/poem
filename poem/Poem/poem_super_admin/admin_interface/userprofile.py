from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm


class SuperUserProfileAdmin(UserAdmin):
    class Media:
        css = {'all': ('/poem_media/css/siteuser.css',)}

    view_on_site = False
    form = UserChangeForm

    fieldsets = [
        (None, {'fields': ['username', 'password']}),
        ('Personal info', {'fields': ['first_name', 'last_name', 'email']}),
        ('Permissions', {'fields': ['is_superuser', 'is_staff', 'is_active']})
    ]

    list_filter = ('is_superuser', 'is_staff',)
    list_display = ('username', 'first_name', 'last_name', 'email',
                    'is_staff', 'is_superuser')
    filter_horizontal = ()
