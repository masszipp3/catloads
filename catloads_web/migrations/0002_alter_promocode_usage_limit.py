# Generated by Django 5.0.6 on 2024-05-12 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catloads_web', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promocode',
            name='usage_limit',
            field=models.IntegerField(blank=True, default=1, help_text='How many times this promo code can be used in total', null=True),
        ),
    ]
