# Generated by Django 2.1.2 on 2018-11-15 01:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ssw', '0025_product_adult_content'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='featured',
            name='contributor',
        ),
        migrations.RemoveField(
            model_name='featured',
            name='product',
        ),
        migrations.AddField(
            model_name='product',
            name='featured',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='requested_to_archive',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='product',
            name='status',
            field=models.CharField(choices=[('pending_approval', 'Pending Approval'), ('pending_admin_approval', 'Pending Admin Approval'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('archived', 'Archived')], default='pending_approval', max_length=255),
        ),
        migrations.DeleteModel(
            name='Featured',
        ),
    ]