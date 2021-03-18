# Generated by Django 3.1.7 on 2021-03-17 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('netapp_manager', '0002_networkservice_developer'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='networkservice',
            constraint=models.UniqueConstraint(fields=('developer', 'identifier'), name='unique_app_identifier_per_developer'),
        ),
    ]
