# Generated by Django 2.0.9 on 2019-04-30 08:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('poem', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='groupsofprobes',
        ),
    ]
