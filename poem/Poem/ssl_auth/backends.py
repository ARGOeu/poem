import re
import logging

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType

from Poem.poem.models import UserProfile
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
    log = logging.getLogger('POEM')
  
    def authenticate(self, request=None):
        if not request:
            return
        
        username = request.META.get(settings.SSL_USERNAME)
        dn = request.META.get(settings.SSL_DN)
        
        if not username or not dn:
            return
        # certificate validation should be done by apache
        profile = UserProfile.objects.filter(subject=dn)       
        # all other cases mean that there was a constraint violation
        # since dn should be unique across all profiles 
        assert len(profile) == 0 or len(profile) == 1
        
        user = None            
        if profile:
            # user is known
            user = profile[0].user
            self.log.debug('authentication succeeds for %s' % str(dn))
        else:
            # user is new
            # try to generate username from CN
            username = self.clean_username(request.META.get(settings.SSL_USERNAME))
            user, created = User.objects.get_or_create(username=username)
            
            if not created:
                # didn't work, same username for different DNs ? hmm ...
                # try generating username from serial
                self.log.debug('failed to generate username from CN for %s' % str(dn))
                username = request.META.get(settings.SSL_SERIAL)[:30]
                user, created = User.objects.get_or_create(username=username)
                
            if not created:
                # didn't work as well, wtf
                # fail as there is no way to generate unique username
                # multiple DNs from the same CA with same CNs ?
                self.log.debug('authentication failure for %s' % str(dn))
                return
            
            # configure new user
            self.configure_user(user, request)

        return user 
        
    def clean_username(self, username):
        # replace spaces with _ and remove all non-word characters
        # auth.User username field is 30 chars
        username = re.sub(r"\s+", '_', username)
        username = re.sub(r"\W", '', username)
        return username[:30]
       
    def configure_user(self, user, request):
        user.set_unusable_password()
        user.is_active = settings.SSL_CREATE_ACTIVE
        user.is_staff = settings.SSL_CREATE_STAFF 
        user.save() 
        
        # user post save event ensures profile is created
        up=user.get_profile()
        up.subject = request.META.get(settings.SSL_DN)
        up.save()
        
        # set default permissions (add/change metric instance, change profile)
#        try:
#            pr_ct = ContentType.objects.get(app_label='poem', model='profile')
#            mi_ct = ContentType.objects.get(app_label='poem', model='metricinstance')
#            user.user_permissions.add(Permission.objects.get(
#                                            codename='change_profile', 
#                                            content_type=pr_ct))
#            user.user_permissions.add(Permission.objects.get(
#                                            codename='change_metricinstance',
#                                            content_type=mi_ct))
#            user.user_permissions.add(Permission.objects.get(
#                                            codename='add_metricinstance',
#                                            content_type=mi_ct))
#            user.save()
#        except Exception, e:
#            self.log.debug('failed to set default permissions for %s' % str(up.subject))
            
        return user
    