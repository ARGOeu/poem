from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save, pre_save

class UserProfile(models.Model):
    """
    Extension of auth.User model that adds certificate DN.
    """
    # This field is required.
    user = models.OneToOneField(User)

    # Other fields here
    # last_login = models.DateTimeField(blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True, unique=True)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

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
    owner = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=1024, blank=True, null=True)

    class Meta:
        ordering = ['name', 'version']
        unique_together = ('name', 'version')
        permissions = (('custowners', 'Profile own'),)

    def __unicode__(self):
        return u'%s %s %s' % (self.name, self.version, self.vo)
                                 #self.valid_from, self.valid_to)
class Group(Group):
    profiles = models.ManyToManyField(Profile, null=True, blank=True)

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
