# Generated by Django 2.1.2 on 2018-10-26 20:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ssw', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='exclusive',
            field=models.BooleanField(default=False),
        ),
    ]