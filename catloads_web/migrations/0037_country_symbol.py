# Generated by Django 5.0.6 on 2024-09-19 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catloads_web', '0036_alter_countryprice_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='symbol',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
