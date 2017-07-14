from Poem import settings
from Poem.poem.dbmodels.probes import Probe
from django import forms
from django.dispatch import receiver
from django.contrib import auth
from django.contrib.auth.hashers import (check_password, make_password, is_password_usable)
from django.contrib.auth.models import UserManager, GroupManager, Permission, PermissionsMixin, AbstractBaseUser
from django.core import validators
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_delete
from django.utils import timezone
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
import re
import copy
import json

from reversion.models import Version

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
    config = models.CharField(max_length=1024)
    attribute = models.CharField(max_length=1024)
    dependancy = models.CharField(max_length=1024)
    flags = models.CharField(max_length=1024)
    parameter = models.CharField(max_length=1024)

    class Meta:
        app_label = 'poem'
        unique_together = (('name', 'probeversion'),)
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
    key = models.CharField(max_length=128)
    value = models.CharField(max_length=128)
    metric = models.ForeignKey(Metric, blank=False, null=False)

    class Meta:
        app_label = 'poem'

def delete_entryfield(*args, **kwargs):
    i = kwargs['instance']
    deletedentry = '{0} {1}'.format(i.key, i.value)
    fielddata = json.loads(i.metric.config)
    if deletedentry in fielddata:
        fielddata.remove(deletedentry)
        i.metric.config = json.dumps(fielddata)
        i.metric.save()
post_delete.connect(delete_entryfield, sender=MetricConfig)
