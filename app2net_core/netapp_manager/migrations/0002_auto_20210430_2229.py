# Generated by Django 3.1.7 on 2021-04-30 22:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import netapp_manager.models.network_service


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('netapp_manager', '0001_squashed_0007_auto_20210430_2218'),
    ]

    operations = [
        migrations.CreateModel(
            name='NetApp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.SlugField(blank=True, max_length=100)),
                ('version', models.CharField(blank=True, max_length=30)),
                ('downloads', models.PositiveIntegerField(default=0, editable=False)),
                ('nad_file', models.FileField(blank=True, null=True, upload_to=netapp_manager.models.network_service.get_nad_upload_path)),
                ('categories', models.ManyToManyField(related_name='network_services', to='netapp_manager.Category')),
                ('conflicts', models.ManyToManyField(related_name='_netapp_conflicts_+', to='netapp_manager.NetApp')),
                ('developer', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='networkservicepackage',
            name='network_service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='packages', to='netapp_manager.netapp', verbose_name='Network Service'),
        ),
        migrations.DeleteModel(
            name='NetworkService',
        ),
        migrations.AddConstraint(
            model_name='netapp',
            constraint=models.UniqueConstraint(fields=('developer', 'identifier'), name='unique_app_identifier_per_developer'),
        ),
    ]
