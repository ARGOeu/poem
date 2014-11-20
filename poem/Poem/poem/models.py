from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save

# from taggit.managers import TaggableManager
# from taggit.utils import edit_string_for_tags

# from Poem.poem.taggit_ext import TaggitFilterSpec

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

# class Extension(models.Model):
#     id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=100, blank=True, null=True)
#
#     class Meta:
#         ordering = ['name']
#
#     def __unicode__(self):
#         return u'%s' % (self.name)
#
# class AvailabilityExpression(Extension):
#     expr = models.CharField(max_length=255,
#                             help_text='Availability calculation formula.')
#     expr_type = models.CharField(max_length=255)
#
#     class Meta:
#         ordering = ['expr', 'expr_type']
#
#     def __unicode__(self):
#         return u'%s %s' % (self.expr, self.expr_type)

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
    #tags = TaggableManager()
    #metric_instances = models.ManyToManyField(MetricInstance,
    #                           help_text='Set of metrics to run in this profile.')
    #groups = models.ManyToManyField(GroupReference, blank=True, null=True,
    #                help_text='Set of ATP groups on which to run the metrics (defined via VO feed).')
    #extensions = models.ManyToManyField(Extension, related_name='provider',
    #                           null=True, blank=True,
    #                           help_text='Set of profile\'s extensions, e.g. availability formula')
    #valid = models.BooleanField(default=True)

    vo = models.CharField(max_length=128,
                    help_text='', verbose_name='VO')
    #valid_from = models.DateTimeField(blank=True, null=True)
    #valid_to = models.DateTimeField(blank=True, null=True)
    owner = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=1024, blank=True, null=True)

    #def formatted_tags(self):
    #    """ Helper method to access formated list of tags that have
    #    proper escape sequences. """
    #    return edit_string_for_tags(self.tags.all())
    #formatted_tags.short_description = 'Tags'

    class Meta:
        ordering = ['name', 'version']
        unique_together = ('name', 'version')

    def __unicode__(self):
        return u'%s %s %s' % (self.name, self.version, self.vo)
                                 #self.valid_from, self.valid_to)

class MetricInstance(models.Model):
    """
    Metric instance is a tuple: (flavour, metric_name, vo, fqan).
    """
    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile, related_name='metric_instances')
    service_flavour = models.CharField(max_length=128)
    metric = models.CharField(max_length=128)
    vo = models.CharField(max_length=128, blank=True, null=True)
    fqan = models.CharField(verbose_name='FQAN', max_length=128, blank=True, null=True,
                            help_text='FQAN used to run the probe.')

    class Meta:
        ordering = ['service_flavour', 'metric', 'vo', 'fqan']
        unique_together = ('profile', 'service_flavour', 'metric', 'fqan')
        permissions = (('readonly', 'Can read only'),)

    def __unicode__(self):
        return u'%s %s %s %s' % (self.service_flavour, self.metric,
                              self.fqan, self.vo)

# workaround for default metric instance VO
def mi_default_vo(sender, instance, **kwargs):
    instance.vo=instance.profile.vo

pre_save.connect(mi_default_vo, sender=MetricInstance)


# class GroupReference(models.Model):
#     id = models.AutoField(primary_key=True)
#     profile = models.ForeignKey(Profile, related_name='groups')
#     atp_grouptype = models.CharField(max_length=100, blank=True, null=True,
#                     verbose_name='Group Type',
#                     help_text='ATP group type (defined via VO feed, hints shown ' +\
#                     'do not contain all the existing types).')
#     atp_groupname = models.CharField(max_length=100, blank=True, null=True,
#                     verbose_name='Group Name',
#                     help_text='ATP group name (defined via VO feed, hints shown ' +\
#                     'do not contain all the existing groups.).')
#     is_deleted = models.CharField(max_length=1, choices= YESNO_CHOICE, default='N')
#     description = models.CharField(max_length=255, null=True, blank=True)
#
#     class Meta:
#         ordering = ['atp_grouptype', 'atp_groupname']
#         unique_together = ('profile', 'atp_grouptype', 'atp_groupname')
#
#     def __unicode__(self):
#         return u'%s %s' % (self.atp_grouptype, self.atp_groupname)

