from django.contrib import admin


class LogEntryAdmin(admin.ModelAdmin):
    class Media:
        css = {"all": ("/poem_media/css/siteactions.css",
                       "/poem_media/ajax_select/css/ajax_select.css")}
        js = ("/poem_media/ajax_select/js/ajax_select.js",
              "/poem_media/ajax_select/js/bootstrap.js")

    def log_entry_name(obj):
        return obj.__str__()
    log_entry_name.short_description = 'Log entry'

    def new_change_message(self, obj):
        return obj.__str__()
    new_change_message.short_description = 'change message'

    list_display = (log_entry_name, 'user', 'action_time')
    fields = ('content_type', 'user', 'action_time', 'object_repr',
              'new_change_message')
    readonly_fields = (
        'content_type',
        'user',
        'action_time',
        'object_repr',
        'new_change_message'
    )
    search_fields = ['user__username']
    date_hierarchy = 'action_time'

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super(LogEntryAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions


    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        Overriding admin.ModelAdmin change_view so that it doesn't show save
        button in change_view
        """
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = False
        return super(LogEntryAdmin, self).change_view(request, object_id,
                                                      form_url, extra_context=extra_context)
