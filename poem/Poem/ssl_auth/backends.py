import re
import logging

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from Poem.poem.models import UserProfile, CustUser
import Poem.django_logging

class SSLBackend(ModelBackend):
    """Django backend that authenticates users against SSL_CLIENT certificate. It
    creates an auth.user model instances based on the information extracted from DN.
    Created user is a valid Django auth.user model with corresponding permissions, roles, etc.
    This auth backend requires ssl_auth.middleware to be installed.

    Configuration:
     * setting.SSL_USERNAME determines the username (defaults to SSL_CLIENT_S_DN_CN).
     * settings.SSL_CREATE_ACTIVE determines a new user active role.
     * settings.SSL_CREATE_STAFF determines a new user staff role.
     * setting.SSL_DN determines user's DN (defaults to SSL_CLIENT_S_DN).
    """
    log = logging.getLogger('POEMAUTHBACK')

    def authenticate(self, request=None):
        if not request:
            return

        username = request.META.get(settings.SSL_USERNAME)
        dn = request.META.get(settings.SSL_DN)

        if not username or not dn:
            return

        try:
            userprof = get_user_model().objects.get(userprofile__subject=dn)

        except CustUser.DoesNotExist:
            # user is new
            # try to generate username from CN
            username = self.clean_username(request.META.get(settings.SSL_USERNAME))
            if '_' in username:
                first, last = username.split('_', 1)
                user, created = get_user_model().objects.get_or_create(username=username,
                                                        first_name=first,
                                                        last_name=last)
            else:
                user, created = get_user_model().objects.get_or_create(username=username)

            if not created:
                # didn't work, same username for different DNs ? hmm ...
                # try generating username from serial
                self.log.error('SSL - failed to generate username from CN for %s' % str(dn))
                username = request.META.get(settings.SSL_SERIAL)[:30]
                user, created = get_user_model().objects.get_or_create(username=username)
                if not created:
                    # didn't work as well, wtf
                    # fail as there is no way to generate unique username
                    # multiple DNs from the same CA with same CNs ?
                    self.log.error('SSL - authentication failure for %s' % str(dn))
                    return

            # configure new user
            self.configure_user(user, request)
            return user

        return userprof

    def clean_username(self, username):
        # replace spaces with _ and remove all non-word characters
        # auth.User username field is 30 chars
        username = re.sub(r"\s+", '_', username)
        return username[:30]

    def configure_user(self, user, request):
        user.set_unusable_password()
        user.is_active = settings.SSL_CREATE_ACTIVE
        user.is_staff = settings.SSL_CREATE_STAFF
        user.save()

        # user post save event ensures profile is created
        up, created = UserProfile.objects.get_or_create(user=user)
        if created:
            up.subject = request.META.get(settings.SSL_DN)
            up.save()
        else:
            self.log.error('SSL - failed to set default permissions for %s' % str(up.subject))

        try:
            user.save()
        except Exception as e:
            self.log.error('SSL - failed to set default permissions for %s' % str(up.subject))

        return user
