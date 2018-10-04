# Generated by Django 2.1 on 2018-08-20 02:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ssw', '0008_auto_20180820_0511'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contributor',
            name='id_image',
        ),
        migrations.AddField(
            model_name='contributor',
            name='photo_id',
            field=models.FileField(blank=True, null=True, upload_to='photo_id/'),
        ),
        migrations.AlterField(
            model_name='contributor',
            name='description_about_artist',
            field=models.TextField(blank=True, null=True),
        ),
    ]
