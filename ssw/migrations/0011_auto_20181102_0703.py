# Generated by Django 2.1.2 on 2018-11-02 04:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ssw', '0010_product_eps_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contributor',
            name='status',
            field=models.CharField(choices=[('unverified', 'Unverified'), ('verified', 'Verified')], default='unverified', max_length=255),
        ),
    ]
