# Generated by Django 2.1.2 on 2018-10-27 03:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ssw', '0004_auto_20181027_0602'),
    ]

    operations = [
        migrations.AlterField(
            model_name='earning',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=5),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=5),
        ),
        migrations.AlterField(
            model_name='payment',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=5),
        ),
    ]
