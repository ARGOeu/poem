from django.contrib import admin


class LogEntryAdmin(admin.ModelAdmin):
    class Media:
        css = {"all": ("/poem_media/css/siteactions.css",)}

    def log_entry_name(obj):
        return obj.__str__()
    log_entry_name.short_description = 'Log entry'

    list_display = (log_entry_name, 'user', 'action_time')
    readonly_fields = (
        'content_type',
        'user',
        'action_time',
        'object_id',
        'object_repr',
        'action_flag',
        'change_message'
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super(LogEntryAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions
