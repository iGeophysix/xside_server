# Generated by Django 4.0 on 2021-12-25 09:01

import client_space.models
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('areas', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326, verbose_name='Areas to show')),
                ('is_active', models.BooleanField(default=False, verbose_name='Item is active')),
                ('max_rate', models.DecimalField(decimal_places=2, default=10, max_digits=8, verbose_name='Maximum Show Rate')),
                ('max_daily_spend', models.DecimalField(decimal_places=2, default=100, max_digits=11, verbose_name='Maximum Daily Spends')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='client_space.client')),
            ],
            options={
                'unique_together': {('client', 'name')},
                'index_together': {('client', 'name')},
            },
        ),
        migrations.CreateModel(
            name='ItemFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.FileField(upload_to=client_space.models.client_directory_path, verbose_name='image')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='client_space.item')),
            ],
        ),
        migrations.CreateModel(
            name='ClientUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client', models.ManyToManyField(to='client_space.Client')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
        ),
    ]
