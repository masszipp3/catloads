# Generated by Django 5.0.6 on 2024-06-24 11:31

import django_ckeditor_5.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catloads_web', '0025_alter_productsale_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productsale',
            name='description',
            field=django_ckeditor_5.fields.CKEditor5Field(blank=True, null=True, verbose_name='Text'),
        ),
    ]
