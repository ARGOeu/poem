from gettext import gettext
import json

from django.contrib import admin
from django.utils.text import get_text_list

from Poem.poem.models import *


def get_new_logentry_name(obj):
    if obj.is_addition():
        return gettext('Added "%(object)s".' % {'object': obj.object_repr})
    elif obj.is_change():
        return gettext('Changed "%(object)s".' % {'object': obj.object_repr})
    elif obj.is_deletion():
        return gettext('Deleted "%(object)s".' % {'object': obj.object_repr})


def get_object_from_db(obj):
    obj = obj.split(' ')
    model = obj[0]
    pk = obj[2][1:-1]  # because the number is in parenthesis
    if pk == 'None':
        return ''
    else:
        if model in ['MetricDependancy', 'MetricFlags', 'MetricFiles',
                     'MetricParameter', 'MetricFileParameter',
                     'MetricAttribute', 'MetricConfig']:
            code = 'obj_repr = %s.objects.get(id=%s).key' % (model, pk)
        elif model in ['MetricParent', 'MetricProbeExecutable']:
            code = 'obj_repr = %s.objects.get(id=%s).value' % (model, pk)
        else:
            code = 'obj_repr = %s.objects.get(id=%s).name' % (model, pk)
        exec(code, globals())
        return obj_repr


def get_new_change_message(obj):
    if obj.content_type.model in ['profile', 'API key', 'groupofmetrics']:
        return obj.__str__()
    else:
        if obj.change_message and obj.change_message[0] == '[':
            try:
                change_message = json.loads(obj.change_message)
            except json.JSONDecodeError:
                return obj.change_message
            messages = []
            for sub_message in change_message:
                if 'added' in sub_message:
                    if sub_message['added']:
                        sub_message['added']['name'] = \
                            gettext(sub_message['added']['name'])
                        if get_object_from_db(gettext(sub_message['added'][
                                                          'object'])):
                            messages.append(gettext('Added %s "%s".')
                                            % (sub_message['added']['name'],
                                               get_object_from_db(
                                                   gettext(sub_message[
                                                               'added'][
                                                               'object'])
                                               )))
                        else:
                            messages.append(gettext('Added a %s.'
                                                    % sub_message['added'][
                                                        'name']))
                    else:
                        messages.append(gettext('Added %s.' % obj.object_repr))
                elif 'changed' in change_message:
                    sub_message['changed']['fields'] = get_text_list(
                        sub_message['changed']['fields'], gettext('and')
                    )
                    if 'name' in sub_message['changed']:
                        sub_message['changed']['name'] = gettext(
                            sub_message['changed']['name']
                        )
                        messages.append(
                            gettext('Changed %s for %s "%s".'
                                    % (sub_message['changed']['fields'],
                                       sub_message['changed']['name'],
                                       get_object_from_db(
                                           gettext(sub_message['changed'][
                                               'object'])
                                       ))
                                    )
                        )
                    else:
                        messages.append(gettext('Changed {fields}.').format(
                            **sub_message['changed']))
                elif 'deleted' in sub_message:
                    sub_message['deleted']['name'] = gettext(
                        sub_message['deleted']['name']
                    )
                    messages.append(gettext('Deleted a %s.')
                                    % sub_message['deleted']['name'])

            change_message = ' '.join(msg[0].upper() + msg[1:] for msg in messages)
            return change_message
        else:
            return obj.change_message


class LogEntryAdmin(admin.ModelAdmin):
    class Media:
        css = {"all": ("/poem_media/css/siteactions.css",
                       "/poem_media/ajax_select/css/ajax_select.css")}
        js = ("/poem_media/ajax_select/js/ajax_select.js",
              "/poem_media/ajax_select/js/bootstrap.js")

    def log_entry_name(obj):
        return get_new_logentry_name(obj)
    log_entry_name.short_description = 'Log entry'

    def new_change_message(self, obj):
        return get_new_change_message(obj)
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
