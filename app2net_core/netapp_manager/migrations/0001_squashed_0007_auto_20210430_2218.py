# Generated by Django 3.1.7 on 2021-04-30 22:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import netapp_manager.models.network_service
import uuid


class Migration(migrations.Migration):

    replaces = [('netapp_manager', '0001_initial'), ('netapp_manager', '0002_networkservicepackage_execution_environment'), ('netapp_manager', '0003_auto_20210410_0228'), ('netapp_manager', '0004_auto_20210410_0447'), ('netapp_manager', '0005_remove_networkservicepackage_requirements'), ('netapp_manager', '0006_auto_20210416_1444'), ('netapp_manager', '0007_auto_20210430_2218')]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('infrastructure_handler', '0001_initial'),
        ('infrastructure_handler', '0002_auto_20210407_2208'),
    ]

    operations = [
        migrations.CreateModel(
            name='NetworkService',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.SlugField(blank=True, max_length=100)),
                ('version', models.CharField(blank=True, max_length=30)),
                ('downloads', models.PositiveIntegerField(default=0, editable=False)),
                ('nad_file', models.FileField(blank=True, null=True, upload_to=netapp_manager.models.network_service.get_nad_upload_path)),
                ('developer', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('address', models.CharField(max_length=300)),
                ('public_key', models.FileField(blank=True, null=True, upload_to='nacr_keys/')),
            ],
            options={
                'verbose_name': 'Repository',
                'verbose_name_plural': 'Repositories',
            },
        ),
        migrations.CreateModel(
            name='NetworkServicePackage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('NetApp', 'NetApp'), ('VNA', 'VNA')], default='NetApp', max_length=6)),
                ('location_flag', models.CharField(choices=[('I', 'Ingress'), ('E', 'Egress'), ('B', 'Border'), ('C', 'Custom'), ('A', 'All')], max_length=1)),
                ('file_path', models.CharField(max_length=500)),
                ('hash', models.CharField(max_length=100)),
                ('nacr', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='network_services', to='netapp_manager.repository')),
                ('network_service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='packages', to='netapp_manager.networkservice', verbose_name='Network Service')),
                ('requirements', models.ManyToManyField(blank=True, to='infrastructure_handler.Resource')),
                ('technology', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='infrastructure_handler.programmabletechnology')),
            ],
        ),
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('command', models.TextField()),
                ('native_procedure', models.BooleanField(blank=True)),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actions', to='netapp_manager.networkservicepackage')),
            ],
        ),
        migrations.AddConstraint(
            model_name='networkservice',
            constraint=models.UniqueConstraint(fields=('developer', 'identifier'), name='unique_app_identifier_per_developer'),
        ),
        migrations.AddConstraint(
            model_name='action',
            constraint=models.UniqueConstraint(fields=('name', 'package'), name='unique_action_name_per_package'),
        ),
        migrations.AddField(
            model_name='networkservicepackage',
            name='execution_environment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='infrastructure_handler.executionenvironment'),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='networkservice',
            name='categories',
            field=models.ManyToManyField(related_name='network_services', to='netapp_manager.Category'),
        ),
        migrations.RemoveField(
            model_name='networkservicepackage',
            name='technology',
        ),
        migrations.AddField(
            model_name='networkservice',
            name='conflicts',
            field=models.ManyToManyField(related_name='_networkservice_conflicts_+', to='netapp_manager.NetworkService'),
        ),
        migrations.RemoveField(
            model_name='networkservicepackage',
            name='requirements',
        ),
        migrations.AlterField(
            model_name='networkservicepackage',
            name='location_flag',
            field=models.CharField(choices=[('ingress', 'Ingress'), ('egress', 'Egress'), ('border', 'Border'), ('custom', 'Custom'), ('all', 'All')], max_length=7),
        ),
        migrations.AddConstraint(
            model_name='networkservicepackage',
            constraint=models.UniqueConstraint(fields=('network_service', 'execution_environment'), name='single_package_per_execution_environment'),
        ),
    ]