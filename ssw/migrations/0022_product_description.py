# Generated by Django 2.1 on 2018-09-17 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ssw', '0021_auto_20180914_2142'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
