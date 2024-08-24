# Generated by Django 5.0.6 on 2024-08-21 12:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catloads_web', '0035_productsale_countries'),
    ]

    operations = [
        migrations.AlterField(
            model_name='countryprice',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_country', to='catloads_web.product'),
        ),
    ]
