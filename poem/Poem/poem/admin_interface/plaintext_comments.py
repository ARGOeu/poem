from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import get_text_list
from Poem.poem.models import Metric, Probe, UserProfile, VO, ServiceFlavour, \
    GroupOfProbes, CustUser, Tags, Metrics, GroupOfMetrics, MetricAttribute, \
    MetricConfig, MetricParameter, MetricFlags, MetricDependancy, \
    MetricProbeExecutable, MetricFiles, MetricParent, MetricFileParameter,\
                             MetricType
from reversion.models import Version
from gettext import gettext
import json


def get_obj_from_db(objname, version, model, object_id):
    """Get object name from the database by its id. In case the object is
    deleted (id = None, ObjectDoesNotExist exception), version queryset is
    loaded for that object and object name is obtained from previous
    version."""

    objname = objname.split(' ')
    try:
        fieldname = eval("%s.objects.get(id=%s)" % (objname[0],
                                                    objname[2][1:-1]
                                                    )
                         )
        if objname[0] == 'MetricProbeExecutable' or objname[0] == \
                'MetricParent':
            return fieldname.value
        else:
            return fieldname.key

    except ObjectDoesNotExist:

        versionset = Version.objects.get_for_object_reference(model, object_id)
        versionid = [i.id for i in versionset if i == version]
        allversionid = [i.id for i in versionset]
        olderversionid = versionset[allversionid.index(versionid[0]) + 1]
        fieldnameold = eval("json.loads(Version.objects.get("
                            "id=%s).serialized_data)[0]['fields']" %
                            olderversionid.id)
        fieldname = eval("json.loads(Version.objects.get("
                         "id=%s).serialized_data)[0]['fields']" % version.id)
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


def get_new_comment(version, model, object_id):
    """
    Function was made as modified version of LogEntry.get_change_message(
    ) function. It makes string change messages from default json in
    reversion_revision database. get_obj_from_db() function is used to
    get the names of changed attributes from database.
    """
    new_comment = version.revision.comment
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
                    messages.append('Added %s "%s".'
                                    % (
                                        sub_message['added']['name'],
                                        get_obj_from_db(gettext(sub_message[
                                                                    'added']
                                                                ['object']
                                                                ), version,
                                                        model,
                                                        object_id)
                                    ))
                else:
                    messages.append('Initial version.')
                    break

            elif 'changed' in sub_message:
                sub_message['changed']['fields'] = get_text_list \
                    (
                        sub_message['changed']['fields'], gettext('and')
                    )
                if 'name' in sub_message['changed']:
                    sub_message['changed']['name'] = gettext(
                        sub_message['changed']['name']
                    )
                    messages.append('Changed %s for %s "%s".'
                                    % (sub_message['changed']['fields'],
                                       gettext(
                                           sub_message['changed']['name']
                                       ),
                                       get_obj_from_db(gettext(
                                           sub_message['changed']['object']
                                       ), version, model, object_id)))
                else:
                    messages.append(gettext('Changed {fields}.').format(
                        **sub_message['changed']
                    )
                    )

            elif 'deleted' in sub_message:
                sub_message['deleted']['name'] = gettext(
                    sub_message['deleted']['name']
                )
                messages.append(
                    'Deleted %s "%s".' % (
                        sub_message['deleted']['name'],
                        get_obj_from_db(gettext(sub_message['deleted']['object']
                                                ), version, model, object_id
                                        )
                    )
                )

        new_comment = ' '.join(msg[0].upper() + msg[1:] for msg in messages)

    return new_comment or gettext('No fields changed.')
