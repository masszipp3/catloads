# Generated by Django 5.0.6 on 2024-06-24 11:22

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catloads_web', '0024_alter_productsale_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productsale',
            name='description',
            field=ckeditor.fields.RichTextField(blank=True, null=True),
        ),
    ]