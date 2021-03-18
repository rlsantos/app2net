# Generated by Django 3.1.7 on 2021-03-18 14:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure_handler', '0006_auto_20210317_1825'),
        ('netapp_manager', '0006_auto_20210317_2040'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='repository',
            options={'verbose_name': 'Repository', 'verbose_name_plural': 'Repositories'},
        ),
        migrations.AddField(
            model_name='networkservice',
            name='downloads',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='networkservice',
            name='version',
            field=models.CharField(default='', max_length=30),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='InstalledNetworkService',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('installation_date', models.DateTimeField(auto_now_add=True)),
                ('update_date', models.DateTimeField(auto_now=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='infrastructure_handler.device')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='netapp_manager.networkservice')),
            ],
        ),
        migrations.AddField(
            model_name='networkservice',
            name='devices',
            field=models.ManyToManyField(blank=True, editable=False, related_name='installed_services', through='netapp_manager.InstalledNetworkService', to='infrastructure_handler.Device'),
        ),
    ]