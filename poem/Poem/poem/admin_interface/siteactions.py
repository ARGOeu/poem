from django.contrib import admin


class LogEntryAdmin(admin.ModelAdmin):
    class Media:
        css = {"all": ("/poem_media/css/siteactions.css",)}

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

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super(LogEntryAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions
