from django.db import models
import reversion
from Poem.poem.models import Probe

class ExtRevision(models.Model):
    class Meta:
        app_label = 'poem'

    version = models.CharField(max_length=128, null=False, help_text='Version')
    probeid = models.BigIntegerField()
    revision = models.OneToOneField(reversion.models.Revision)

def on_revision_commit(instances, **kwargs):
    if isinstance(instances[0], Probe):
        ExtRevision.objects.create(probeid=instances[0].id, version=instances[0].version, revision=kwargs['revision'])
        instances[0].datetime = kwargs['revision'].date_created
        instances[0].save()
reversion.post_revision_commit.connect(on_revision_commit)
