# Generated by Django 5.0.6 on 2024-05-13 13:51

import catloads_web.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catloads_web', '0011_productsale_sale_id'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='customuser',
            managers=[
                ('objects', catloads_web.models.UserManager()),
            ],
        ),
    ]
