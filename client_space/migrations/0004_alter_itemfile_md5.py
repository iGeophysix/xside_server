# Generated by Django 4.0 on 2022-01-06 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client_space', '0003_itemfile_md5'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemfile',
            name='md5',
            field=models.CharField(default='', max_length=32, verbose_name='image md5'),
        ),
    ]
