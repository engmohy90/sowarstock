# Generated by Django 2.1.2 on 2018-11-15 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ssw', '0028_sowarstockuser_suspended'),
    ]

    operations = [
        migrations.AddField(
            model_name='sowarstockuser',
            name='suspension_reason',
            field=models.TextField(blank=True, null=True),
        ),
    ]
