# Generated by Django 3.1.7 on 2021-02-20 21:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('command', models.TextField()),
                ('params', models.TextField(blank=True)),
                ('uploadable', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='AddressType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Credential',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50, null=True)),
                ('password', models.CharField(max_length=50, null=True)),
                ('key', models.FileField(null=True, upload_to='pvn_credentials')),
                ('access_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='credentials', to='infrastructure_handler.accesstype')),
            ],
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('FAILED', 'Failed')], default='active', max_length=20)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('update_date', models.DateTimeField(auto_now=True)),
                ('credentials', models.ManyToManyField(related_name='devices', to='infrastructure_handler.Credential', verbose_name='Available Credentials')),
            ],
        ),
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('version', models.CharField(max_length=20)),
                ('status', models.CharField(choices=[('STABLE', 'Stable Version'), ('TESTING', 'Testing Version'), ('UNSTABLE', 'Unstable Version'), ('DEVELOPMENT', 'Development Version'), ('FUTURE', 'Future Version')], default='active', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Interface',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interfaces', to='infrastructure_handler.device')),
            ],
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('status', models.CharField(choices=[('ESTABLISH', 'Established'), ('FAILED', 'Failed')], default='active', max_length=10)),
                ('max_speed', models.PositiveIntegerField(help_text='Insert the max speed of the link')),
                ('unity', models.CharField(choices=[('KB', 'KiloBytes'), ('GHZ', 'GHz')], help_text='Choose the measurement unit for the resource', max_length=10)),
                ('interface', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='infrastructure_handler.interface')),
            ],
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('value', models.CharField(help_text='Specify the frequency, speed, clock, quantity, capacity or version of the resource', max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='ResourceType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('unity', models.CharField(choices=[('KB', 'KiloBytes'), ('GHZ', 'GHz')], help_text='Choose the measurement unit for the resource', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='External',
            fields=[
                ('link_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='infrastructure_handler.link')),
                ('internet_access', models.BooleanField(default=False)),
                ('observations', models.TextField(null=True)),
            ],
            bases=('infrastructure_handler.link',),
        ),
        migrations.CreateModel(
            name='Logical',
            fields=[
                ('resource_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='infrastructure_handler.resource')),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('FAILED', 'Failed')], default='active', max_length=20)),
            ],
            bases=('infrastructure_handler.resource',),
        ),
        migrations.CreateModel(
            name='Physical',
            fields=[
                ('resource_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='infrastructure_handler.resource')),
                ('manufacturer', models.CharField(max_length=50, null=True)),
                ('model', models.CharField(max_length=50, null=True)),
            ],
            bases=('infrastructure_handler.resource',),
        ),
        migrations.AddField(
            model_name='resource',
            name='resource_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='infrastructure_handler.resourcetype'),
        ),
        migrations.CreateModel(
            name='Pvn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('owner', models.ManyToManyField(related_name='pvns', to=settings.AUTH_USER_MODEL, verbose_name='PVN Owner')),
            ],
        ),
        migrations.CreateModel(
            name='ProgrammableTechnology',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('version', models.CharField(max_length=20)),
                ('resources', models.ManyToManyField(related_name='programmable_technologies', to='infrastructure_handler.Resource', verbose_name='Resources of Programmable Technology')),
            ],
        ),
        migrations.CreateModel(
            name='InstalledDrivers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('install_driver_date', models.DateTimeField(auto_now_add=True)),
                ('update_driver_date', models.DateTimeField(auto_now=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='installed_drivers', to='infrastructure_handler.device')),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='installations', to='infrastructure_handler.driver')),
            ],
        ),
        migrations.AddField(
            model_name='device',
            name='drivers',
            field=models.ManyToManyField(related_name='devices', through='infrastructure_handler.InstalledDrivers', to='infrastructure_handler.Driver', verbose_name='List of Drivers'),
        ),
        migrations.AddField(
            model_name='device',
            name='programmable_technologies',
            field=models.ManyToManyField(to='infrastructure_handler.ProgrammableTechnology', verbose_name='Available Programmable Technologies'),
        ),
        migrations.AddField(
            model_name='device',
            name='pvn',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='devices', to='infrastructure_handler.pvn'),
        ),
        migrations.AddField(
            model_name='device',
            name='resources',
            field=models.ManyToManyField(related_name='devices', to='infrastructure_handler.Resource', verbose_name='List of Available Resources'),
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=128)),
                ('mask', models.PositiveSmallIntegerField(help_text='Insert the mask in the CIDR notation', null=True)),
                ('address_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to='infrastructure_handler.addresstype')),
                ('interface', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to='infrastructure_handler.interface')),
            ],
        ),
        migrations.CreateModel(
            name='Internal',
            fields=[
                ('link_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='infrastructure_handler.link')),
                ('destination', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='infrastructure_handler.interface')),
            ],
            bases=('infrastructure_handler.link',),
        ),
    ]