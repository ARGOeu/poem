# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Probe'
        db.create_table(u'poem_probe', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=28)),
            ('nameversion', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('repository', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('docurl', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('group', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('user', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(max_length=32, null=True, blank=True)),
        ))
        db.send_create_signal('poem', ['Probe'])

        # Adding model 'GroupOfProbes'
        db.create_table(u'poem_groupofprobes', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=80)),
        ))
        db.send_create_signal('poem', ['GroupOfProbes'])

        # Adding M2M table for field permissions on 'GroupOfProbes'
        m2m_table_name = db.shorten_name(u'poem_groupofprobes_permissions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('groupofprobes', models.ForeignKey(orm['poem.groupofprobes'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(m2m_table_name, ['groupofprobes_id', 'permission_id'])

        # Adding M2M table for field probes on 'GroupOfProbes'
        m2m_table_name = db.shorten_name(u'poem_groupofprobes_probes')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('groupofprobes', models.ForeignKey(orm['poem.groupofprobes'], null=False)),
            ('probe', models.ForeignKey(orm['poem.probe'], null=False))
        ))
        db.create_unique(m2m_table_name, ['groupofprobes_id', 'probe_id'])

        # Adding model 'Profile'
        db.create_table(u'poem_profile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('version', self.gf('django.db.models.fields.CharField')(default='1.0', max_length=10)),
            ('vo', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('groupname', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('poem', ['Profile'])

        # Adding unique constraint on 'Profile', fields ['name', 'version']
        db.create_unique(u'poem_profile', ['name', 'version'])

        # Adding model 'GroupOfProfiles'
        db.create_table(u'poem_groupofprofiles', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=80)),
        ))
        db.send_create_signal('poem', ['GroupOfProfiles'])

        # Adding M2M table for field permissions on 'GroupOfProfiles'
        m2m_table_name = db.shorten_name(u'poem_groupofprofiles_permissions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('groupofprofiles', models.ForeignKey(orm['poem.groupofprofiles'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(m2m_table_name, ['groupofprofiles_id', 'permission_id'])

        # Adding M2M table for field profiles on 'GroupOfProfiles'
        m2m_table_name = db.shorten_name(u'poem_groupofprofiles_profiles')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('groupofprofiles', models.ForeignKey(orm['poem.groupofprofiles'], null=False)),
            ('profile', models.ForeignKey(orm['poem.profile'], null=False))
        ))
        db.create_unique(m2m_table_name, ['groupofprofiles_id', 'profile_id'])

        # Adding model 'VO'
        db.create_table(u'poem_vo', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, primary_key=True)),
        ))
        db.send_create_signal('poem', ['VO'])

        # Adding model 'ServiceFlavour'
        db.create_table(u'poem_serviceflavour', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
        ))
        db.send_create_signal('poem', ['ServiceFlavour'])

        # Adding model 'MetricInstance'
        db.create_table(u'poem_metricinstance', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(related_name='metric_instances', to=orm['poem.Profile'])),
            ('service_flavour', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('metric', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('vo', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('fqan', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
        ))
        db.send_create_signal('poem', ['MetricInstance'])

        # Adding unique constraint on 'MetricInstance', fields ['profile', 'service_flavour', 'metric', 'fqan']
        db.create_unique(u'poem_metricinstance', ['profile_id', 'service_flavour', 'metric', 'fqan'])

        # Adding model 'Metrics'
        db.create_table(u'poem_metrics', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('poem', ['Metrics'])

        # Adding model 'Tags'
        db.create_table(u'poem_tags', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('poem', ['Tags'])

        # Adding model 'GroupOfMetrics'
        db.create_table(u'poem_groupofmetrics', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=80)),
        ))
        db.send_create_signal('poem', ['GroupOfMetrics'])

        # Adding M2M table for field permissions on 'GroupOfMetrics'
        m2m_table_name = db.shorten_name(u'poem_groupofmetrics_permissions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('groupofmetrics', models.ForeignKey(orm['poem.groupofmetrics'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(m2m_table_name, ['groupofmetrics_id', 'permission_id'])

        # Adding M2M table for field metrics on 'GroupOfMetrics'
        m2m_table_name = db.shorten_name(u'poem_groupofmetrics_metrics')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('groupofmetrics', models.ForeignKey(orm['poem.groupofmetrics'], null=False)),
            ('metrics', models.ForeignKey(orm['poem.metrics'], null=False))
        ))
        db.create_unique(m2m_table_name, ['groupofmetrics_id', 'metrics_id'])

        # Adding model 'Metric'
        db.create_table(u'poem_metric', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poem.Tags'])),
            ('probeversion', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('probekey', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['reversion.Version'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poem.GroupOfMetrics'])),
            ('probeexecutable', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('config', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('attribute', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('dependancy', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('flags', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('parameter', self.gf('django.db.models.fields.CharField')(max_length=1024)),
        ))
        db.send_create_signal('poem', ['Metric'])

        # Adding unique constraint on 'Metric', fields ['name', 'tag']
        db.create_unique(u'poem_metric', ['name', 'tag_id'])

        # Adding model 'MetricDependancy'
        db.create_table(u'poem_metricdependancy', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('metric', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poem.Metric'])),
        ))
        db.send_create_signal('poem', ['MetricDependancy'])

        # Adding model 'MetricFlags'
        db.create_table(u'poem_metricflags', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('metric', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poem.Metric'])),
        ))
        db.send_create_signal('poem', ['MetricFlags'])

        # Adding model 'MetricParameter'
        db.create_table(u'poem_metricparameter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('metric', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poem.Metric'])),
        ))
        db.send_create_signal('poem', ['MetricParameter'])

        # Adding model 'MetricAttribute'
        db.create_table(u'poem_metricattribute', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('metric', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poem.Metric'])),
        ))
        db.send_create_signal('poem', ['MetricAttribute'])

        # Adding model 'MetricConfig'
        db.create_table(u'poem_metricconfig', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('metric', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poem.Metric'])),
        ))
        db.send_create_signal('poem', ['MetricConfig'])

        # Adding model 'MetricProbeExecutable'
        db.create_table(u'poem_metricprobeexecutable', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('metric', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['poem.Metric'])),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('poem', ['MetricProbeExecutable'])

        # Adding model 'CustUser'
        db.create_table(u'poem_custuser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('poem', ['CustUser'])

        # Adding M2M table for field user_permissions on 'CustUser'
        m2m_table_name = db.shorten_name(u'poem_custuser_user_permissions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('custuser', models.ForeignKey(orm['poem.custuser'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(m2m_table_name, ['custuser_id', 'permission_id'])

        # Adding M2M table for field groupsofprofiles on 'CustUser'
        m2m_table_name = db.shorten_name(u'poem_custuser_groupsofprofiles')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('custuser', models.ForeignKey(orm['poem.custuser'], null=False)),
            ('groupofprofiles', models.ForeignKey(orm['poem.groupofprofiles'], null=False))
        ))
        db.create_unique(m2m_table_name, ['custuser_id', 'groupofprofiles_id'])

        # Adding M2M table for field groupsofmetrics on 'CustUser'
        m2m_table_name = db.shorten_name(u'poem_custuser_groupsofmetrics')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('custuser', models.ForeignKey(orm['poem.custuser'], null=False)),
            ('groupofmetrics', models.ForeignKey(orm['poem.groupofmetrics'], null=False))
        ))
        db.create_unique(m2m_table_name, ['custuser_id', 'groupofmetrics_id'])

        # Adding M2M table for field groupsofprobes on 'CustUser'
        m2m_table_name = db.shorten_name(u'poem_custuser_groupsofprobes')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('custuser', models.ForeignKey(orm['poem.custuser'], null=False)),
            ('groupofprobes', models.ForeignKey(orm['poem.groupofprobes'], null=False))
        ))
        db.create_unique(m2m_table_name, ['custuser_id', 'groupofprobes_id'])

        # Adding model 'UserProfile'
        db.create_table(u'poem_userprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['poem.CustUser'], unique=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True, null=True, blank=True)),
        ))
        db.send_create_signal('poem', ['UserProfile'])

        # Adding model 'ExtRevision'
        db.create_table(u'poem_extrevision', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('probeid', self.gf('django.db.models.fields.BigIntegerField')()),
            ('revision', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['reversion.Revision'], unique=True)),
        ))
        db.send_create_signal('poem', ['ExtRevision'])


    def backwards(self, orm):
        # Removing unique constraint on 'Metric', fields ['name', 'tag']
        db.delete_unique(u'poem_metric', ['name', 'tag_id'])

        # Removing unique constraint on 'MetricInstance', fields ['profile', 'service_flavour', 'metric', 'fqan']
        db.delete_unique(u'poem_metricinstance', ['profile_id', 'service_flavour', 'metric', 'fqan'])

        # Removing unique constraint on 'Profile', fields ['name', 'version']
        db.delete_unique(u'poem_profile', ['name', 'version'])

        # Deleting model 'Probe'
        db.delete_table(u'poem_probe')

        # Deleting model 'GroupOfProbes'
        db.delete_table(u'poem_groupofprobes')

        # Removing M2M table for field permissions on 'GroupOfProbes'
        db.delete_table(db.shorten_name(u'poem_groupofprobes_permissions'))

        # Removing M2M table for field probes on 'GroupOfProbes'
        db.delete_table(db.shorten_name(u'poem_groupofprobes_probes'))

        # Deleting model 'Profile'
        db.delete_table(u'poem_profile')

        # Deleting model 'GroupOfProfiles'
        db.delete_table(u'poem_groupofprofiles')

        # Removing M2M table for field permissions on 'GroupOfProfiles'
        db.delete_table(db.shorten_name(u'poem_groupofprofiles_permissions'))

        # Removing M2M table for field profiles on 'GroupOfProfiles'
        db.delete_table(db.shorten_name(u'poem_groupofprofiles_profiles'))

        # Deleting model 'VO'
        db.delete_table(u'poem_vo')

        # Deleting model 'ServiceFlavour'
        db.delete_table(u'poem_serviceflavour')

        # Deleting model 'MetricInstance'
        db.delete_table(u'poem_metricinstance')

        # Deleting model 'Metrics'
        db.delete_table(u'poem_metrics')

        # Deleting model 'Tags'
        db.delete_table(u'poem_tags')

        # Deleting model 'GroupOfMetrics'
        db.delete_table(u'poem_groupofmetrics')

        # Removing M2M table for field permissions on 'GroupOfMetrics'
        db.delete_table(db.shorten_name(u'poem_groupofmetrics_permissions'))

        # Removing M2M table for field metrics on 'GroupOfMetrics'
        db.delete_table(db.shorten_name(u'poem_groupofmetrics_metrics'))

        # Deleting model 'Metric'
        db.delete_table(u'poem_metric')

        # Deleting model 'MetricDependancy'
        db.delete_table(u'poem_metricdependancy')

        # Deleting model 'MetricFlags'
        db.delete_table(u'poem_metricflags')

        # Deleting model 'MetricParameter'
        db.delete_table(u'poem_metricparameter')

        # Deleting model 'MetricAttribute'
        db.delete_table(u'poem_metricattribute')

        # Deleting model 'MetricConfig'
        db.delete_table(u'poem_metricconfig')

        # Deleting model 'MetricProbeExecutable'
        db.delete_table(u'poem_metricprobeexecutable')

        # Deleting model 'CustUser'
        db.delete_table(u'poem_custuser')

        # Removing M2M table for field user_permissions on 'CustUser'
        db.delete_table(db.shorten_name(u'poem_custuser_user_permissions'))

        # Removing M2M table for field groupsofprofiles on 'CustUser'
        db.delete_table(db.shorten_name(u'poem_custuser_groupsofprofiles'))

        # Removing M2M table for field groupsofmetrics on 'CustUser'
        db.delete_table(db.shorten_name(u'poem_custuser_groupsofmetrics'))

        # Removing M2M table for field groupsofprobes on 'CustUser'
        db.delete_table(db.shorten_name(u'poem_custuser_groupsofprobes'))

        # Deleting model 'UserProfile'
        db.delete_table(u'poem_userprofile')

        # Deleting model 'ExtRevision'
        db.delete_table(u'poem_extrevision')


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
            'config': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'dependancy': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'flags': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poem.GroupOfMetrics']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'parameter': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'probeexecutable': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'probekey': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['reversion.Version']"}),
            'probeversion': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poem.Tags']"})
        },
        'poem.metricattribute': {
            'Meta': {'object_name': 'MetricAttribute'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'metric': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poem.Metric']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'poem.metricconfig': {
            'Meta': {'object_name': 'MetricConfig'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'metric': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poem.Metric']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'poem.metricdependancy': {
            'Meta': {'object_name': 'MetricDependancy'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'metric': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poem.Metric']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'poem.metricflags': {
            'Meta': {'object_name': 'MetricFlags'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'metric': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poem.Metric']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '128'})
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
            'key': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'metric': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poem.Metric']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'poem.metricprobeexecutable': {
            'Meta': {'object_name': 'MetricProbeExecutable'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metric': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['poem.Metric']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '128'})
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
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