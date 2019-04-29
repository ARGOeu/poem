from django import forms
from django.contrib import admin


class TenantForm(forms.ModelForm):
    name = forms.CharField(help_text='Tenant name.',
                           max_length=128,
                           label='Name')
    domain_url = forms.CharField(help_text='Host for this tenant.',
                                 max_length=128,
                                 label='Hostname')
    created_on = forms.CharField(help_text='Date when the tenant was added.',
                                 max_length=64,
                                 required=False)


class TenantAdmin(admin.ModelAdmin):
    form = TenantForm
    list_display = ('name', 'domain_url', 'created_on')

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.fields = ('name', 'domain_url', 'created_on',)
            self.readonly_fields = ('created_on',)

        else:
            self.fields = ('name', 'domain_url',)

        return super().get_form(request, obj=None, **kwargs)
