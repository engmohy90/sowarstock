# Generated by Django 2.1 on 2018-08-17 18:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ssw', '0005_auto_20180817_1919'),
    ]

    operations = [
        migrations.RenameField(
            model_name='address',
            old_name='street1',
            new_name='address1',
        ),
        migrations.RenameField(
            model_name='address',
            old_name='street2',
            new_name='address2',
        ),
    ]
