# Generated by Django 4.0 on 2022-01-06 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client_space', '0002_alter_itemfile_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemfile',
            name='md5',
            field=models.CharField(default='', max_length=16, verbose_name='image md5'),
        ),
    ]
