# Generated by Django 2.1.2 on 2018-11-12 13:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ssw', '0021_auto_20181112_0640'),
    ]

    operations = [
        migrations.RenameField(
            model_name='review',
            old_name='read_by_owner',
            new_name='read_by_product_owner',
        ),
    ]
