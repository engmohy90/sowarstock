# Generated by Django 2.1 on 2018-08-15 19:06

from django.db import migrations, models
import django.db.models.deletion
import django_mysql.models
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ssw', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_id', models.IntegerField()),
                ('title', models.CharField(max_length=255)),
                ('image', easy_thumbnails.fields.ThumbnailerImageField(upload_to='products/')),
                ('released', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('pending_approval', 'Pending Approval'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending_approval', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('keywords', django_mysql.models.ListCharField(models.CharField(max_length=255), max_length=10, size=None)),
                ('category', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='ssw.Category')),
            ],
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('main_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ssw.Category')),
            ],
        ),
        migrations.AlterModelOptions(
            name='contributor',
            options={'verbose_name': 'Contributor User'},
        ),
        migrations.AlterModelOptions(
            name='sowarstockuser',
            options={'verbose_name': 'Sowar Stock User'},
        ),
        migrations.AddField(
            model_name='product',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ssw.Contributor'),
        ),
        migrations.AddField(
            model_name='product',
            name='subcategory',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='ssw.SubCategory'),
        ),
    ]
