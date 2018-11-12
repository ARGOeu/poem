from django import template
from django.utils.text import get_text_list
from django.core.exceptions import ObjectDoesNotExist

from reversion.models import Version

from Poem.poem.models import Metric, Probe, UserProfile, VO, ServiceFlavour, \
    GroupOfProbes, CustUser, Tags, Metrics, GroupOfMetrics, MetricAttribute, \
    MetricConfig, MetricParameter, MetricFlags, MetricDependancy, \
    MetricProbeExecutable, MetricFiles, MetricParent, MetricFileParameter,\
                             MetricType

from gettext import gettext
import json

register = template.Library()


def get_obj_from_db(objname, object_id, version_id):
    """Get object name from the database by its id. In case the object is
    deleted (id = None, ObjectDoesNotExist exception), version queryset is
    loaded for that object and object name is obtained from previous
    version."""

    objname = objname.split(' ')
    try:
        fieldname = eval("%s.objects.get(id=%s)" % (objname[0], objname[2][
                                                                1:-1]))
        try:
            return fieldname.key
        except AttributeError:
            return fieldname.value

    except ObjectDoesNotExist:

        versionset = Version.objects.all().filter(object_id=object_id)
        versionid = [i.id for i in versionset if i.id == version_id]
        allversionid = [i.id for i in versionset]
        olderversionid = versionset[allversionid.index(versionid[0]) + 1]
        fieldnameold = eval("json.loads(Version.objects.get("
                            "id=%s).serialized_data)[0]['fields']" %
                            olderversionid.id)
        fieldname = eval("json.loads(Version.objects.get("
                         "id=%s).serialized_data)[0]['fields']" % version_id)
        names = {'MetricProbeExecutable': 'probeexecutable',
                 'MetricAttribute': 'attribute',
                 'MetricConfig': 'config',
                 'MetricDependancy': 'dependancy',
                 'MetricParameter': 'parameter',
                 'MetricFlags': 'flags',
                 'MetricFiles': 'files',
                 'MetricFileParameter': 'fileparameter',
                 'MetricParent': 'parent'}
        value = json.loads(fieldname[names[objname[0]]])
        valueold = json.loads(fieldnameold[names[objname[0]]])
        diff_fieldname = list(set(valueold) - set(value))[0].split(' ')[0]

        return diff_fieldname

@register.simple_tag
def get_new_comment(comment, obj_id=None, version_id=None):
    """Makes nicer comments in object_history templates. It makes plaintext
    messages from default json comment in log table."""

    new_comment = comment

    if new_comment and new_comment[0] == '[':
        try:
            new_comment = json.loads(new_comment)
        except json.JSONDecodeError:
            return new_comment

    if 'Derived' in new_comment:
        pass

    else:
        messages = []
        for sub_message in new_comment:
            if 'added' in sub_message:
                if sub_message['added']:
                    sub_message['added']['name'] = gettext(sub_message['added']
                                                           ['name'])
                    if version_id:
                        messages.append('Added %s "%s".' % (sub_message[
                            'added']['name'], get_obj_from_db(gettext(
                            sub_message['added']['object']), obj_id,
                            version_id)))
                    else:
                        messages.append('Added new %s.'
                                        % (sub_message['added']['name']))
                else:
                    messages.append('Initial version.')
                    break

            elif 'changed' in sub_message:
                sub_message['changed']['fields'] = get_text_list \
                    (sub_message['changed']['fields'], gettext('and'))

                if 'name' in sub_message['changed']:
                    sub_message['changed']['name'] = gettext(
                        sub_message['changed']['name'])
                    if version_id:
                        messages.append('Changed %s for %s "%s".' % (
                            sub_message['changed']['fields'], gettext(
                                sub_message['changed']['name']),
                            get_obj_from_db(gettext(sub_message['changed'][
                                                        'object']),
                                            obj_id, version_id)))
                    else:
                        messages.append('Changed %s for %s.'
                                        % (sub_message['changed']['fields'],
                                           gettext(sub_message['changed'][
                                                        'name'])))

                else:
                    messages.append(gettext('Changed {fields}.').format(
                        **sub_message['changed']))

            elif 'deleted' in sub_message:
                sub_message['deleted']['name'] = gettext(
                    sub_message['deleted']['name'])

                if version_id:
                    messages.append('Deleted %s "%s".' % (sub_message[
                        'deleted']['name'], get_obj_from_db(gettext(
                        sub_message['deleted']['object']), obj_id, version_id)))
                else:
                    messages.append('Deleted %s.' % (sub_message['deleted'][
                        'name']))

        new_comment = ' '.join(msg[0].upper() + msg[1:] for msg in messages)

    return new_comment or gettext('No fields changed.')