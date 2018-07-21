# reversion DB schema updates from v 1.8.7

from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import re


class MyMigration(migrations.Migration):
    """ Do the migration of schema for another app listed in
        settings.INSTALLED_APPS whose models are used in poem Django application

        https://stackoverflow.com/questions/29575802/django-migration-file-in-an-other-app/29587968
    """
    def __init__(self, name, app_label):
        name = '0003_reversion_updates'
        app_label = 'reversion'
        super(MyMigration, self).__init__(name, app_label)

    replaces = (('reversion', __module__.rsplit('.', 1)[-1]),)


class Migration(MyMigration):

    initial = False

    dependencies = [
        ('poem', '0002_extrev_add'),
    ]

    operations = [
        migrations.AddField(
            model_name='Version',
            name='db',
            field=models.CharField(default='default', max_length=191,
                                   help_text='The database the model under version control is stored in.'),
        ),
        # Leave extra field from previous django-reversion versions, otherwise
        # migration file will not apply
        #
        # migrations.RemoveField(
        #     model_name='Version',
        #     name='object_id_int',
        # ),
        migrations.AlterUniqueTogether(
            name='Version',
            unique_together={("db", "content_type", "object_id", "revision")},
        ),
        # Leave extra field from previous django-reversion versions, otherwise
        # migration file will not apply
        #
        # migrations.RemoveField(
        #     model_name='Revision',
        #     name='manager_slug',
        # ),
    ]
