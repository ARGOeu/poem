from django import template
from django.utils.text import get_text_list
from gettext import gettext
import json

register = template.Library()


@register.filter(name='get_new_comment')
def get_new_comment(new_comment):
    """Makes nicer comments in object_history templates. It makes plaintext
    messages from default json comment in log table."""

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
                    messages.append('Changed %s for %s.'
                                    % (sub_message['changed']['fields'],
                                       gettext(sub_message['changed']['name'])))

                else:
                    messages.append(gettext('Changed {fields}.').format(
                        **sub_message['changed']))

            elif 'deleted' in sub_message:
                sub_message['deleted']['name'] = gettext(
                    sub_message['deleted']['name'])
                messages.append('Deleted %s.' % (sub_message['deleted']['name'])
                    )

        new_comment = ' '.join(msg[0].upper() + msg[1:] for msg in messages)

    return new_comment or gettext('No fields changed.')