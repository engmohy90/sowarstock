# Generated by Django 2.1.2 on 2018-12-21 05:48

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('ssw', '0052_auto_20181221_0830'),
    ]

    operations = [
        migrations.AddField(
            model_name='userrequest',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
