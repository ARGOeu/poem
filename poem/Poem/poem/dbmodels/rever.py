from django.db import models
import reversion

class ExtRevision(models.Model):
    class Meta:
        app_label = 'poem'

    version = models.CharField(max_length=128, null=False, help_text='Version')
    revision = models.OneToOneField(reversion.models.Revision)

def on_revision_commit(instances, **kwargs):
    ExtRevision.objects.create(version=instances[0].version, revision=kwargs['revision'])
reversion.post_revision_commit.connect(on_revision_commit)
