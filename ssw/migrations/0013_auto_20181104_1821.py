# Generated by Django 2.1.2 on 2018-11-04 15:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ssw', '0012_auto_20181104_1753'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sowarstockuser',
            name='country_code',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='countries_plus.Country'),
        ),
    ]
