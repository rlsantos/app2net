# Generated by Django 3.1.7 on 2021-04-16 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure_handler', '0003_auto_20210410_0228'),
    ]

    operations = [
        migrations.AddField(
            model_name='executionenvironment',
            name='version',
            field=models.CharField(default='1.0', max_length=30),
            preserve_default=False,
        ),
    ]