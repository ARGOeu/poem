# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MetricFileParameter'
        db.create_table(u'poem_metricfileparameter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=384)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=384)),
            ('metric', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poem.Metric'])),
        ))
        db.send_create_signal('poem', ['MetricFileParameter'])

        # Adding field 'Metric.fileparameter'
        db.add_column(u'poem_metric', 'fileparameter',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=1024),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'MetricFileParameter'
        db.delete_table(u'poem_metricfileparameter')

        # Deleting field 'Metric.fileparameter'
        db.delete_column(u'poem_metric', 'fileparameter')


    models = {
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'poem.custuser': {
            'Meta': {'object_name': 'CustUser'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groupsofmetrics': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'user_set'", 'blank': 'True', 'to': "orm['poem.GroupOfMetrics']"}),
            'groupsofprobes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'user_set'", 'blank': 'True', 'to': "orm['poem.GroupOfProbes']"}),
            'groupsofprofiles': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'user_set'", 'blank': 'True', 'to': "orm['poem.GroupOfProfiles']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'poem.extrevision': {
            'Meta': {'object_name': 'ExtRevision'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'probeid': ('django.db.models.fields.BigIntegerField', [], {}),
            'revision': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['reversion.Revision']", 'unique': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'poem.groupofmetrics': {
            'Meta': {'object_name': 'GroupOfMetrics'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metrics': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['poem.Metrics']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'poem.groupofprobes': {
            'Meta': {'object_name': 'GroupOfProbes'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'probes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['poem.Probe']", 'null': 'True', 'blank': 'True'})
        },
        'poem.groupofprofiles': {
            'Meta': {'object_name': 'GroupOfProfiles'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'profiles': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['poem.Profile']", 'null': 'True', 'blank': 'True'})
        },
        'poem.metric': {
            'Meta': {'unique_together': "(('name', 'tag'),)", 'object_name': 'Metric'},
            'attribute': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'cloned': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True'}),
            'config': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'dependancy': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'fileparameter': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'files': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'flags': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poem.GroupOfMetrics']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'parameter': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'parent': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'probeexecutable': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'probekey': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['reversion.Version']"}),
            'probeversion': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poem.Tags']"})
        },
        'poem.metricattribute': {
            'Meta': {'object_name': 'MetricAttribute'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '384'}),
            'metric': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poem.Metric']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '384'})
        },
        'poem.metricconfig': {
            'Meta': {'object_name': 'MetricConfig'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '384', 'null': 'True', 'blank': 'True'}),
            'metric': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poem.Metric']", 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '384', 'null': 'True', 'blank': 'True'})
        },
        'poem.metricdependancy': {
            'Meta': {'object_name': 'MetricDependancy'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '384'}),
            'metric': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poem.Metric']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '384'})
        },
        'poem.metricfileparameter': {
            'Meta': {'object_name': 'MetricFileParameter'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '384'}),
            'metric': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poem.Metric']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '384'})
        },
        'poem.metricfiles': {
            'Meta': {'object_name': 'MetricFiles'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '384'}),
            'metric': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poem.Metric']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '384'})
        },
        'poem.metricflags': {
            'Meta': {'object_name': 'MetricFlags'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '384'}),
            'metric': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poem.Metric']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '384'})
        },
        'poem.metricinstance': {
            'Meta': {'ordering': "['service_flavour', 'metric', 'vo', 'fqan']", 'unique_together': "(('profile', 'service_flavour', 'metric', 'fqan'),)", 'object_name': 'MetricInstance'},
            'fqan': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metric': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'metric_instances'", 'to': "orm['poem.Profile']"}),
            'service_flavour': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'vo': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        'poem.metricparameter': {
            'Meta': {'object_name': 'MetricParameter'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '384'}),
            'metric': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poem.Metric']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '384'})
        },
        'poem.metricparent': {
            'Meta': {'object_name': 'MetricParent'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metric': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poem.Metric']", 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '384', 'null': 'True'})
        },
        'poem.metricprobeexecutable': {
            'Meta': {'object_name': 'MetricProbeExecutable'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metric': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poem.Metric']", 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '384', 'null': 'True'})
        },
        'poem.metrics': {
            'Meta': {'object_name': 'Metrics'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'poem.probe': {
            'Meta': {'object_name': 'Probe'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'docurl': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'group': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'nameversion': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'repository': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '28'})
        },
        'poem.profile': {
            'Meta': {'ordering': "['name', 'version']", 'unique_together': "(('name', 'version'),)", 'object_name': 'Profile'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'groupname': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'version': ('django.db.models.fields.CharField', [], {'default': "'1.0'", 'max_length': '10'}),
            'vo': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'poem.serviceflavour': {
            'Meta': {'object_name': 'ServiceFlavour'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'primary_key': 'True'})
        },
        'poem.tags': {
            'Meta': {'object_name': 'Tags'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'poem.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'displayname': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'egiid': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['poem.CustUser']", 'unique': 'True'})
        },
        'poem.vo': {
            'Meta': {'object_name': 'VO'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'primary_key': 'True'})
        },
        u'reversion.revision': {
            'Meta': {'object_name': 'Revision'},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manager_slug': ('django.db.models.fields.CharField', [], {'default': "u'default'", 'max_length': '191', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poem.CustUser']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        u'reversion.version': {
            'Meta': {'object_name': 'Version'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'format': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.TextField', [], {}),
            'object_id_int': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'object_repr': ('django.db.models.fields.TextField', [], {}),
            'revision': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['reversion.Revision']"}),
            'serialized_data': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['poem']