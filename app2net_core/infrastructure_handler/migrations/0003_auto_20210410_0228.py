# Generated by Django 3.1.7 on 2021-04-10 02:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure_handler', '0002_auto_20210407_2208'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='device',
            name='programmable_technologies',
        ),
        migrations.RemoveField(
            model_name='programmabletechnology',
            name='resources',
        ),
        migrations.AlterField(
            model_name='driver',
            name='execution_environments',
            field=models.ManyToManyField(related_name='drivers', to='infrastructure_handler.ExecutionEnvironment'),
        ),
    ]
