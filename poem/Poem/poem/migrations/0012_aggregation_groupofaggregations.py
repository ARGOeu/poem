# Generated by Django 2.0.13 on 2019-02-24 11:10

import django.contrib.auth.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
        ('poem', '0011_extend_dnfield'),
    ]

    operations = [
        migrations.CreateModel(
            name='Aggregation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the Aggregation profile.', max_length=128)),
                ('apiid', models.CharField(help_text='WEB-API ID of Aggregation profile', max_length=128)),
            ],
            options={
                'permissions': (('aggregationsown', 'Read/Write/Modify'),),
            },
        ),
        migrations.CreateModel(
            name='GroupOfAggregations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, unique=True, verbose_name='name')),
                ('aggregations', models.ManyToManyField(blank=True, to='poem.Aggregation')),
                ('permissions', models.ManyToManyField(blank=True, to='auth.Permission', verbose_name='permissions')),
            ],
            options={
                'verbose_name': 'Group of aggregations',
                'verbose_name_plural': 'Groups of aggregations',
            },
            managers=[
                ('objects', django.contrib.auth.models.GroupManager()),
            ],
        ),
    ]
