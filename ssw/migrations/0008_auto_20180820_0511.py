# Generated by Django 2.1 on 2018-08-20 02:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ssw', '0007_auto_20180820_0454'),
    ]

    operations = [
        migrations.AddField(
            model_name='contributor',
            name='description_about_artist',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='contributor',
            name='display_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='contributor',
            name='job_title',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='contributor',
            name='portfolio_url',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
