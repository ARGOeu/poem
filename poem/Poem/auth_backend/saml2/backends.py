from djangosaml2.backends import Saml2Backend
from django.contrib.auth import get_user_model

from unidecode import unidecode

from Poem.poem.models import UserProfile

NAME_TO_OID = {'distinguishedName': 'urn:oid:2.5.4.49',
               'eduPersonUniqueId': 'urn:oid:1.3.6.1.4.1.5923.1.1.1.13'}

class SAML2Backend(Saml2Backend):
    def username_from_displayname(self, displayname):
        ascii_displayname = unidecode(displayname)

        if ' ' in ascii_displayname:
            name = ascii_displayname.split(' ')
            return '_'.join(name)
        else:
            return ascii_displayname


    def username_from_givename_sn(self, firstname, lastname):
        ascii_firstname = unidecode(firstname)
        ascii_lastname = unidecode(lastname)

        if ' ' in ascii_firstname:
            ascii_firstname = '_'.join(ascii_firstname.split(' '))

        if ' ' in ascii_lastname:
            ascii_lastname = '_'.join(ascii_lastname.split(' '))

        return ascii_firstname + '_' + ascii_lastname


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

        displayname, username, first_name, last_name = '', '', '', ''
        try:
            displayname = self.multival_attr(attributes['displayName'])
            username = self.username_from_displayname(displayname)
        except KeyError:
            first_name = self.multival_attr(attributes['givenName'])
            lastname = self.multival_attr(attributes['sn'])
            username = self.username_from_givename_sn(firstname, lastname)

        certsub = ''
        try:
            certsub = attributes[NAME_TO_OID['distinguishedName']][0]
            certsub = self.certsub_rev(certsub)
        except (KeyError, IndexError):
            pass

        email = self.multival_attr(attributes['mail'])
        egiid = self.multival_attr(attributes[NAME_TO_OID['eduPersonUniqueId']])

        userfound, created = None, None
        try:
            userfound = get_user_model().objects.get(username=username)
        except get_user_model().DoesNotExist:
            user, created = get_user_model().objects.get_or_create(username=username,
                                                                   first_name=first_name,
                                                                   last_name=last_name,
                                                                   email=email)

        if created:
            user.set_unusable_password()
            user.is_active = True
            user.is_staff = True
            user.save()

            userpro, upcreated = UserProfile.objects.get_or_create(user=user)
            if upcreated:
                userpro.subject = certsub
                userpro.displayname = displayname
                userpro.egiid = egiid
                userpro.save()
            else:
                raise Exception

            return user

        elif userfound:
            userfound.email = email
            userfound.save()

            userpro = UserProfile.objects.get(user=userfound)
            userpro.displayname = displayname
            userpro.egiid = egiid
            userpro.subject = certsub
            userpro.save()

            return userfound

        else:
            return None
