from django.db import migrations, models
import django.db.models.deletion


def set_passive(apps, schema_editor):
    Metric = apps.get_model('poem', 'Metric')
    MetricType = apps.get_model('poem', 'MetricType')
    mtype = MetricType.objects.get(name='Passive')
    objs = Metric.objects.filter(flags__contains='PASSIVE 1')
    for obj in objs:
        obj.mtype = mtype
        obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('poem', '0005_add_metrictype'),
    ]

    operations = [
        migrations.RunPython(set_passive),
    ]

