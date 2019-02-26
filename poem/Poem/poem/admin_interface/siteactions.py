from gettext import gettext
import json

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.text import get_text_list

from Poem.poem.models import *

from reversion.models import Version, Revision


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
        elif model == 'GroupOfMetrics_metrics':
            code = 'obj_repr = GroupOfMetrics.objects.get(' \
                   'metrics_id=%s).name' % pk
        elif model == 'GroupOfProbes_probes':
            code = 'obj_repr = GroupOfProbes.objects.get(probes__id=%s)' % pk
        elif model == 'GroupOfProfiles_profiles':
            code = 'obj_repr = GroupOfProfiles.objects.get(' \
                   'profiles_id=%s).name' % pk
        else:
            code = 'obj_repr = %s.objects.get(id=%s).name' % (model, pk)
        exec(code, globals())
        return obj_repr


def get_new_change_message(obj):
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
                    if obj.content_type.model == 'profile':
                        messages.append(
                            gettext('Added %s %s (service type: %s).\n')
                            % (sub_message['added']['name'],
                               gettext(
                                   sub_message['added']['object']
                               ).split(' ')[1],
                               gettext(
                                   sub_message['added']['object']
                               ).split(' ')[0])
                        )
                    elif get_object_from_db(
                            gettext(
                                sub_message['added']['object']
                            )
                    ):
                        messages.append(
                            gettext('Added %s "%s".\n')
                            % (sub_message['added']['name'],
                               get_object_from_db(
                                   gettext(sub_message['added']['object'])
                               )
                               )
                        )
                    else:
                        messages.append(
                            gettext('Added a %s.\n'
                                    % sub_message['added']['name'])
                        )
                else:
                    messages.append(gettext('Added %s.' % obj.object_repr))
            elif 'changed' in sub_message:
                sub_message['changed']['fields'] = get_text_list(
                    sub_message['changed']['fields'],
                    gettext('and')
                )
                if 'name' in sub_message['changed']:
                    sub_message['changed']['name'] = gettext(
                        sub_message['changed']['name']
                    )
                    if obj.content_type.model == 'profile':
                        messages.append(
                            gettext('Added %s %s (service type: %s).\n')
                            % (sub_message['changed']['name'],
                               gettext(
                                   sub_message['changed']['object']
                               ).split(' ')[1],
                               gettext(
                                   sub_message['changed']['object']
                               ).split(' ')[0])
                        )
                    else:
                        messages.append(
                            gettext('Changed %s for %s "%s".\n'
                                    % (sub_message['changed']['fields'],
                                       sub_message['changed']['name'],
                                       get_object_from_db(
                                           gettext(
                                               sub_message['changed']['object']
                                           )
                                       )
                                       )
                                    )
                        )
                else:
                    messages.append(
                        gettext(
                            'Changed {fields}.\n'
                        ).format(**sub_message['changed'])
                    )
            elif 'deleted' in sub_message:
                sub_message['deleted']['name'] = gettext(
                    sub_message['deleted']['name']
                )
                if obj.content_type.model == 'profile':
                    messages.append(gettext(
                        'Deleted %s %s (service type: %s).\n'
                    )
                                    % (sub_message['deleted']['name'],
                                       gettext(
                                           sub_message['deleted']['object']
                                       ).split(' ')[1],
                                       gettext(
                                           sub_message['deleted']['object']
                                       ).split(' ')[0])
                                    )
                else:
                    messages.append(
                        gettext(
                            'Deleted a %s.\n'
                        )
                        % sub_message['deleted']['name']
                    )

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

    def obj_repr(self, obj):
        if obj.content_type.model in ('probe', 'metric'):
            vers = Version.objects.filter(
                object_id=obj.object_id,
                object_repr=obj.object_repr,
                content_type_id=obj.content_type.id
            )
            revs = []
            for ver in vers:
                revs.append(Revision.objects.get(id=ver.id).date_created)

            date = min(revs, key=lambda x: abs(x - obj.action_time))
            ver = vers[revs.index(date)]

            url = '/poem/admin/poem/{}/{}/history/{}/'.format(
                obj.content_type.model,
                obj.object_id,
                ver.id
            )
        else:
            url = '/poem/admin/poem/{}/{}/change/'.format(
                obj.content_type.model,
                obj.object_id
            )
        urlrepr = format_html(
            '<a href="{0}">{1}</a>',
            (url),
            obj.object_repr,
        )
        return urlrepr
    obj_repr.short_description = 'object representation'

    list_display = (log_entry_name, 'user', 'action_time')
    list_filter = (
        ('content_type', admin.RelatedOnlyFieldListFilter),
    )
    fields = ('content_type', 'user', 'action_time', 'obj_repr',
              'new_change_message')
    readonly_fields = (
        'content_type',
        'user',
        'action_time',
        'obj_repr',
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
