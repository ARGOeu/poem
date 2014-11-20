from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render_to_response
from django.conf import settings

class ReadPermissionModelAdmin(admin.ModelAdmin):
    """
    Extension for Django admin to support read-only access. Basically the class overrides
    methods of admin.ModelAdmin and adds an attribute to a request identifying a read-only
    access.

    Credits: http://gremu.net/blog/2010/django-admin-read-only-permission/
    """
    def has_change_permission(self, request, obj=None):
        if getattr(request, 'readonly', False):
            return True
        return super(ReadPermissionModelAdmin, self).has_change_permission(request, obj)

    def changelist_view(self, request, extra_context=None):
        try:
            return super(ReadPermissionModelAdmin, self).changelist_view(
                request, extra_context=extra_context)
        except PermissionDenied:
            pass
        if request.method == 'POST':
            return render_to_response('poem/permission_denied.html', {'admin': settings.ADMIN_NAME,
                                                                      'mail': settings.ADMIN_EMAIL})
        request.readonly = True
        return super(ReadPermissionModelAdmin, self).changelist_view(
            request, extra_context=extra_context)

    def change_view(self, request, object_id, extra_context=None):
        try:
            return super(ReadPermissionModelAdmin, self).change_view(
                request, object_id, extra_context=extra_context)
        except PermissionDenied:
            pass
        if request.method == 'POST':
            return render_to_response('poem/permission_denied.html', {'admin': settings.ADMIN_NAME,
                                                                      'mail': settings.ADMIN_EMAIL})
        request.readonly = True
        return super(ReadPermissionModelAdmin, self).change_view(
            request, object_id, extra_context=extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        try:
            return super(ReadPermissionModelAdmin, self).add_view(
                    request, form_url=form_url, extra_context=extra_context)
        except PermissionDenied:
            return render_to_response('poem/permission_denied.html', {'admin': settings.ADMIN_NAME,
                                                                      'mail': settings.ADMIN_EMAIL})
