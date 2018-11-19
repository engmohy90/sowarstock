# Generated by Django 2.1.2 on 2018-11-11 23:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ssw', '0018_sampleproduct'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='products/thumbnails/'),
        ),
        migrations.AlterField(
            model_name='product',
            name='eps_image',
            field=models.ImageField(blank=True, null=True, upload_to='products/'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='products/'),
        ),
        migrations.AlterField(
            model_name='product',
            name='watermark',
            field=models.ImageField(blank=True, null=True, upload_to='products/watermarked/'),
        ),
        migrations.AlterField(
            model_name='sowarstockuser',
            name='address',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ssw.Address'),
        ),
    ]
