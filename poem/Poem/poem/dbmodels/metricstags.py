from django.contrib.auth.models import GroupManager, Permission
from django.db import models
from django.db.models.signals import post_delete
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

import json


from reversion.models import Version, Revision
from reversion import post_revision_commit, pre_revision_commit

class Metrics(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)

    class Meta:
        permissions = (('metricsown', 'Read/Write/Modify'),)
        app_label = 'poem'

    def __unicode__(self):
        return u'%s' % self.name


class Tags(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)

    class Meta:
        app_label = 'poem'

    def __unicode__(self):
        return u'%s' % (self.name)


class GroupOfMetrics(models.Model):
    name = models.CharField(_('name'), max_length=80, unique=True)
    permissions = models.ManyToManyField(Permission,
                                         verbose_name=_('permissions'), blank=True)
    metrics = models.ManyToManyField(Metrics, null=True, blank=True)
    objects = GroupManager()

    class Meta:
        verbose_name = _('Group of metrics')
        verbose_name_plural = _('Groups of metrics')
        app_label = 'poem'

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)


class Metric(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    tag = models.ForeignKey(Tags)
    probeversion = models.CharField(max_length=128)
    probekey = models.ForeignKey(Version)
    group = models.ForeignKey(GroupOfMetrics)
    probeexecutable = models.CharField(max_length=128)
    config = models.CharField(max_length=1024)
    attribute = models.CharField(max_length=1024)
    dependancy = models.CharField(max_length=1024)
    flags = models.CharField(max_length=1024)
    parameter = models.CharField(max_length=1024)
    cloned = models.CharField(max_length=128, null=True)

    class Meta:
        app_label = 'poem'
        unique_together = (('name', 'tag'),)

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.tag)


class MetricDependancy(models.Model):
    key = models.CharField(max_length=128)
    value = models.CharField(max_length=128)
    metric = models.ForeignKey(Metric)

    class Meta:
        app_label = 'poem'


class MetricFlags(models.Model):
    key = models.CharField(max_length=128)
    value = models.CharField(max_length=128)
    metric = models.ForeignKey(Metric)

    class Meta:
        app_label = 'poem'


class MetricParameter(models.Model):
    key = models.CharField(max_length=128)
    value = models.CharField(max_length=128)
    metric = models.ForeignKey(Metric)

    class Meta:
        app_label = 'poem'


class MetricAttribute(models.Model):
    key = models.CharField(max_length=128)
    value = models.CharField(max_length=128)
    metric = models.ForeignKey(Metric)

    class Meta:
        app_label = 'poem'


class MetricConfig(models.Model):
    key = models.CharField(max_length=128, blank=False, null=False)
    value = models.CharField(max_length=128, blank=False, null=False)
    metric = models.ForeignKey(Metric, blank=False, null=False)

    class Meta:
        app_label = 'poem'


class MetricProbeExecutable(models.Model):
    metric = models.ForeignKey(Metric, blank=False, null=False)
    value = models.CharField(max_length=128, null=False,
                            help_text='Probe executable')
    class Meta:
        app_label = 'poem'


def delete_entryfield(*args, **kwargs):
    i = kwargs['instance']
    deletedentry = '{0} {1}'.format(i.key, i.value)
    field = i.__class__.__name__.split('Metric')[1].lower()
    fielddata = json.loads(eval('i.metric.%s' % field))
    if deletedentry in fielddata:
        fielddata.remove(deletedentry)
        codestr = """i.metric.%s = json.dumps(fielddata)""" % field
        exec codestr
        i.metric.save()

post_delete.connect(delete_entryfield, sender=MetricAttribute)
post_delete.connect(delete_entryfield, sender=MetricConfig)
post_delete.connect(delete_entryfield, sender=MetricDependancy)
post_delete.connect(delete_entryfield, sender=MetricFlags)
post_delete.connect(delete_entryfield, sender=MetricParameter)

# delete empty revision leftover created by delete_entryfield()
# on deletion of parent Metric record. such leftover revision
# is created with empty comment.
def delete_leftover_revision(instances, **kwargs):
    if len(instances) == 1 and isinstance(instances[0], Metric):
        rev = kwargs['revision']
        if rev.comment:
            pass
        else:
            rev.delete()
    else:
        pass

post_revision_commit.connect(delete_leftover_revision)

already_called = False
def copy_derived_metric(instances, **kwargs):
    global already_called
    if len(instances) == 1 and isinstance(instances[0], Metric):
        if instances[0].cloned and not already_called:
            derived_id = int(instances[0].cloned)
            ct = ContentType.objects.get_for_model(Metric)
            derived_vers = Version.objects.filter(object_id_int=derived_id,
                                                  content_type_id=ct.id)
            for v in derived_vers:
                rev = Revision.objects.get(pk=v.revision_id)
                copy_rev = Revision.objects.create(manager_slug=rev.manager_slug,
                                                   date_created=rev.date_created,
                                                   user_id=rev.user_id,
                                                   comment=rev.comment)
                Revision.objects.filter(pk=copy_rev.id).update(date_created=rev.date_created)
                ver = Version.objects.create(revision_id=copy_rev.id,
                                             object_id=str(instances[0].id),
                                             object_id_int=instances[0].id,
                                             content_type_id=ct.id,
                                             format=v.format,
                                             serialized_data=v.serialized_data,
                                             object_repr=repr(instances[0]))
                data = json.loads(ver.serialized_data)[0]
                data['pk'] = instances[0].id
                ver.serialized_data = json.dumps([data])
                ver.save()
    already_called = True

pre_revision_commit.connect(copy_derived_metric)
