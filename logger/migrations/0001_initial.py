# Generated by Django 4.0 on 2022-01-08 19:56

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('client_space', '0006_alter_item_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoModule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='Module name')),
                ('phone', models.CharField(blank=True, max_length=10, null=True, verbose_name='Phone number (10 digits)')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('point', django.contrib.gis.db.models.fields.PointField(srid=4326, verbose_name='Log geo location')),
                ('event', models.CharField(choices=[('S', 'Start'), ('SH', 'Show'), ('P', 'Stop'), ('WA', 'Warning'), ('ER', 'Error')], max_length=2)),
                ('data', models.JSONField(blank=True, null=True, verbose_name='Other log data')),
                ('item_file', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='client_space.itemfile', verbose_name='Shown Item File')),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='logger.videomodule')),
            ],
        ),
    ]