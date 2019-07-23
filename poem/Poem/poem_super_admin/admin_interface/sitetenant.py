from django import forms
from django.contrib import admin
from Poem.poem.models import GroupOfMetrics
from tenant_schemas.utils import schema_context


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
    class Media:
        css = {'all': ('/poem_media/css/sitetenant.css',)}

    form = TenantForm
    list_display = ('name', 'domain_url', 'created_on')

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.fields = ('name', 'domain_url', 'created_on',)
            self.readonly_fields = ('created_on',)

        else:
            self.fields = ('name', 'domain_url',)

        return super().get_form(request, obj=None, **kwargs)

    def save_model(self, request, obj, form, change):
        """
        Creating new tenant. After the tenant and tenant's schema are created,
        GroupOfMetrics with the same name (upper case) is created in the
        tenant schema.
        """
        obj.schema_name = obj.name.lower()
        if request.user.is_superuser:
            obj.save()

            with schema_context(obj.schema_name):
                GroupOfMetrics.objects.create(name=obj.schema_name.upper())
