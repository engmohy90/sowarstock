# Generated by Django 2.1.2 on 2018-11-14 05:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ssw', '0022_auto_20181112_1635'),
    ]

    operations = [
        migrations.AddField(
            model_name='sampleproduct',
            name='viewed_by_admin',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='sampleproduct',
            name='viewed_by_reviewer',
            field=models.BooleanField(default=False),
        ),
    ]
