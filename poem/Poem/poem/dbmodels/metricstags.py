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

class MetricsProbe(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    tag = models.ForeignKey(Tags)
    probever = models.ForeignKey(Probe)
    config = models.CharField(max_length=128)
    docurl = models.CharField(max_length=128)
    group = models.ForeignKey(GroupOfMetrics)

    class Meta:
        app_label = 'poem'
        unique_together = (('name', 'probever'),)
    def __unicode__(self):
        return u'%s %s' % (self.name, self.probever)
