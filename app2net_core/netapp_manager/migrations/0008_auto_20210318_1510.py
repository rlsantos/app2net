# Generated by Django 3.1.7 on 2021-03-18 15:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('netapp_manager', '0007_auto_20210318_1454'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='networkservice',
            name='devices',
        ),
        migrations.DeleteModel(
            name='InstalledNetworkService',
        ),
    ]
