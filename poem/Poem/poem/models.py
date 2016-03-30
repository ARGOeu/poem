from Poem import settings
from django import forms
from django.dispatch import receiver
from django.contrib import auth
from django.contrib.auth.hashers import (check_password, make_password, is_password_usable)
from django.contrib.auth.models import UserManager, GroupManager, Permission, PermissionsMixin, AbstractBaseUser
from django.core import validators
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import m2m_changed, pre_save, post_save
from django.utils import timezone
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
import re

YESNO_CHOICE= ((u'Y',u'Yes'), (u'N', u'No'),)

class VO(models.Model):
    name = models.CharField(max_length=128, help_text='', verbose_name='Virtual organization', \
                            primary_key=True)

    def __unicode__(self):
        return u'%s' % self.name

class ServiceFlavour(models.Model):
    name = models.CharField(max_length=128, help_text='', verbose_name='Service flavour', \
                            primary_key=True)
    description = models.CharField(max_length=1024, blank=True, null=True)

    def __unicode__(self):
        return u'%s' % self.name

class Probe(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128, null=False,
                    help_text='Name of the probe.')
    version = models.CharField(max_length=128, null=False, help_text='Version of the probe.')
    nameversion = models.CharField(max_length=128, null=False, help_text='Name, version tuple.')
    description = models.CharField(max_length=1024, blank=True, null=True)

    class Meta:
        permissions = (('probesown', 'Read/Write/Modify'),)

    def __unicode__(self):
        return u'%s %s' % (self.name, self.version)

@receiver(pre_save, sender=Probe)
def probe_handler(sender, instance, **kwargs):
    instance.nameversion = str(instance.name) + '-' + str(instance.version)

class Profile(models.Model):
    """
    Profile is the core model and is defined as a set of metric instances, where
    metric instance is a tuple (flavour, metric_name, vo, fqan).

    Additional attributes cover profile's name, version, tags, ownership, defining VO and
    description.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128, null=False,
                    help_text='Name of the profile.')
    version = models.CharField(max_length=10, null=False, default='1.0',
                               help_text='Multiple versions of the profile can exist (defaults to 1.0).')
    vo = models.CharField(max_length=128,
                    help_text='', verbose_name='VO')
    description = models.CharField(max_length=1024, blank=True, null=True)

    class Meta:
        ordering = ['name', 'version']
        unique_together = ('name', 'version')
        permissions = (('profileown', 'Read/Write/Modify'),)

    def __unicode__(self):
        return u'%s %s %s' % (self.name, self.version, self.vo)

class Metrics(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)

    class Meta:
        permissions = (('metricsown', 'Read/Write/Modify'),)

class Tags(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)

class MetricsProbe(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    tag = models.CharField(max_length=128)
    probever = models.ForeignKey(Probe)
    config = models.CharField(max_length=128)
    docurl = models.CharField(max_length=128)
    group = models.CharField(max_length=128)


class MetricInstance(models.Model):
    """
    Metric instance is a tuple: (flavour, metric_name, vo, fqan).
    """
    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile, related_name='metric_instances')
    service_flavour = models.CharField(max_length=128)
    metric = models.CharField(max_length=128)
    vo = models.CharField(max_length=128, blank=True, null=True)
    fqan = models.CharField(verbose_name='FQAN', max_length=128, blank=True, null=True)

    class Meta:
        ordering = ['service_flavour', 'metric', 'vo', 'fqan']
        unique_together = ('profile', 'service_flavour', 'metric', 'fqan')

    def __unicode__(self):
        return u'%s %s %s %s' % (self.service_flavour, self.metric,
                              self.fqan, self.vo)

# workaround for default metric instance VO
def mi_default_vo(sender, instance, **kwargs):
    instance.vo=instance.profile.vo
pre_save.connect(mi_default_vo, sender=MetricInstance)

class GroupOfProbes(models.Model):
    name = models.CharField(_('name'), max_length=80, unique=True)
    permissions = models.ManyToManyField(Permission,
                                         verbose_name=_('permissions'), blank=True)
    probes = models.ManyToManyField(Probe, null=True, blank=True)
    objects = GroupManager()

    class Meta:
        verbose_name = _('Group of probes')
        verbose_name_plural = _('Groups of probes')

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)

class GroupOfProfiles(models.Model):
    name = models.CharField(_('name'), max_length=80, unique=True)
    permissions = models.ManyToManyField(Permission,
                                         verbose_name=_('permissions'), blank=True)
    profiles = models.ManyToManyField(Profile, null=True, blank=True)
    objects = GroupManager()

    class Meta:
        verbose_name = _('Group of profiles')
        verbose_name_plural = _('Groups of profiles')

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)

class GroupOfMetrics(models.Model):
    name = models.CharField(_('name'), max_length=80, unique=True)
    permissions = models.ManyToManyField(Permission,
                                         verbose_name=_('permissions'), blank=True)
    metrics = models.ManyToManyField(Metrics, null=True, blank=True)
    objects = GroupManager()

    class Meta:
        verbose_name = _('Group of metrics')
        verbose_name_plural = _('Groups of metrics')

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)

class CustPermissionsMixin(models.Model):
    is_superuser = models.BooleanField(_('superuser status'), default=False,
        help_text=_('Designates that this user has all permissions without '
                    'explicitly assigning them.'))
    user_permissions = models.ManyToManyField(Permission,
        verbose_name=_('user permissions'), blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="user_set", related_query_name="user")
    groupsofprofiles = models.ManyToManyField(GroupOfProfiles, verbose_name=('groups of profiles'),
        blank=True, help_text=_('The groups of profiles that this user belongs to'),
        related_name='user_set', related_query_name='user')
    groupsofmetrics = models.ManyToManyField(GroupOfMetrics, verbose_name=('groups of metrics'),
        blank=True, help_text=_('The groups of metrics that this user belongs to'),
        related_name='user_set', related_query_name='user')
    groupsofprobes = models.ManyToManyField(GroupOfProbes, verbose_name=('groups of probes'),
        blank=True, help_text=_('The groups of probes that this user belongs to'),
        related_name='user_set', related_query_name='user')

    class Meta:
        abstract = True

    def _user_get_all_permissions(self, user, obj):
        permissions = set()
        for backend in auth.get_backends():
            if hasattr(backend, "get_all_permissions"):
                permissions.update(backend.get_all_permissions(user, obj))
        return permissions

    def _user_has_module_perms(self, user, app_label):
        for backend in auth.get_backends():
            if hasattr(backend, "has_module_perms"):
                if backend.has_module_perms(user, app_label):
                    return True
        return False

    def _user_has_perm(self, user, perm, obj):
        for backend in auth.get_backends():
            if hasattr(backend, "has_perm"):
                if backend.has_perm(user, perm, obj):
                    return True
        return False

    def get_group_permissions(self, obj=None):
        permissions = set()
        for backend in auth.get_backends():
            if hasattr(backend, "get_group_permissions"):
                permissions.update(backend.get_group_permissions(self, obj))
        return permissions

    def get_all_permissions(self, obj=None):
        return self._user_get_all_permissions(self, obj)

    def has_perm(self, perm, obj=None):
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        # Otherwise we need to check the backends.
        return self._user_has_perm(self, perm, obj)

    def has_perms(self, perm_list, obj=None):
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True

    def has_module_perms(self, app_label):
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        return self._user_has_module_perms(self, app_label)

# class CustAbstractUser(AbstractBaseUser, CustPermissionsMixin):
class CustAbstractBaseUser(AbstractBaseUser, CustPermissionsMixin):
    class Meta:
        abstract = True
    pass

class CustAbstractUser(CustAbstractBaseUser):
    class Meta:
        abstract = True
    pass

class CustUser(CustAbstractUser):
    username = models.CharField(_('username'), max_length=30, unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, numbers and '
                    '@/./+/-/_ characters'),
        validators=[
            validators.RegexValidator(re.compile('^[\w.@+-]+$'), _('Enter a valid username.'), 'invalid')
        ])
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.username)

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

class UserProfile(models.Model):
    """
    Extension of auth.User model that adds certificate DN.
    """
    # This field is required.
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    subject = models.CharField(max_length=255, blank=True, null=True, unique=True)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
post_save.connect(create_user_profile, sender=settings.AUTH_USER_MODEL)
