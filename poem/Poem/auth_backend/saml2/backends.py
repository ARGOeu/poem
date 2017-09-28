from djangosaml2.backends import Saml2Backend
from django.contrib.auth import get_user_model

from Poem.poem.models import UserProfile

NAME_TO_OID = {'distinguishedName': 'urn:oid:2.5.4.49'}

class SAML2Backend(Saml2Backend):
    def username_from_cn(self, cnval):
        if ' ' in cnval:
            parts = cnval.split(' ')
            parts = filter(lambda x: '@' not in x, parts)

            return '_'.join(parts)
        else:
            return cnval


    def certsub_rev(self, certsubject, retlist=False):
        attrs = certsubject.split('/')
        attrs.reverse()

        if retlist:
            return attrs[:-1]
        else:
            return ','.join(attrs[:-1])


    def multival_attr(self, attr):
        if len(attr) > 1:
            return ' '.join(attr)
        elif len(attr) == 1:
            return attr[0]


    def authenticate(self, session_info=None, attribute_mapping=None,
                     create_unknown_user=True):
        attributes = session_info['ava']
        certsub = attributes[NAME_TO_OID['distinguishedName']][0]
        certsubl = self.certsub_rev(certsub, retlist=True)

        cn_val = certsubl[0].split('=')[1]
        username = self.username_from_cn(cn_val)

        certsub = self.certsub_rev(certsub)

        userprof, created = None, None
        try:
            userprof = get_user_model().objects.get(userprofile__subject=certsub)
        except get_user_model().DoesNotExist:
            user, created = get_user_model().objects.get_or_create(username=username,
                                                                   first_name=self.multival_attr(attributes['givenName']),
                                                                   last_name=self.multival_attr(attributes['sn']),
                                                                   email=self.multival_attr(attributes['mail']))
        if created:
            user.set_unusable_password()
            user.is_active = True
            user.is_staff = True
            user.save()

            up, upcreated = UserProfile.objects.get_or_create(user=user)
            if upcreated:
                up.subject = certsub
                up.save()
            else:
                raise Exception

            return user

        elif userprof:
            return userprof

        else:
            return None
