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
    rev = kwargs['revision']

    if (len(instances) == 1
        and isinstance(instances[0], Probe)):
        ExtRevision.objects.create(probeid=instances[0].id, version=instances[0].version, revision=rev)
        instances[0].datetime = rev.date_created
        instances[0].save()
    # delete extra revision that plugin creates with empty comment
    if rev.id and not rev.comment:
        rev.delete()

reversion.post_revision_commit.connect(on_revision_commit)
