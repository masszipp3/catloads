# Generated by Django 5.0.6 on 2024-09-21 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catloads_web', '0041_cartitem_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]
