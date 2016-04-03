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
from django.db.models.signals import m2m_changed, pre_save, post_save
from django.utils import timezone
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
import re
import copy

class Metrics(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    group = models.CharField(max_length=128)

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

class MetricsProbe(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    tag = models.ForeignKey(Tags)
    probever = models.ForeignKey(Probe)
    config = models.CharField(max_length=128)
    docurl = models.CharField(max_length=128)
    group = models.CharField(max_length=128)

    class Meta:
        app_label = 'poem'
        unique_together = (('name', 'probever'),)
    def __unicode__(self):
        return u'%s %s' % (self.name, self.probever)

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

wasmetrics = []
def gpmetric_presave(sender, instance, **kwargs):
    global wasmetrics
    if instance.pk:
        wasmetrics = copy.copy(instance.metrics.values_list('pk', flat=True))
    else:
       wasmetrics = []
pre_save.connect(gpmetric_presave, sender=GroupOfMetrics)
def gpmetric_m2m(sender, action, pk_set, instance, **kwargs):
    global wasmetrics
    if action == 'post_clear':
        for m in wasmetrics:
           Metrics.objects.filter(id=m).update(group='')
    if action == 'post_add':
        for m in pk_set:
            Metrics.objects.filter(id=m).update(group=instance.name)
m2m_changed.connect(gpmetric_m2m, sender=GroupOfMetrics.metrics.through)
