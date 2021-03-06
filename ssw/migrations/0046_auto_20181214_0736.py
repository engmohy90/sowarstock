# Generated by Django 2.1.2 on 2018-12-14 04:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ssw', '0045_product_editorial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='eps_image',
        ),
        migrations.AlterField(
            model_name='product',
            name='status',
            field=models.CharField(choices=[('pending_approval', 'Pending Approval'), ('pending_admin_approval', 'Pending Admin Approval'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('archived', 'Archived')], default='pending_admin_approval', max_length=255),
        ),
    ]
