# Generated by Django 5.0.6 on 2024-06-04 07:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catloads_web', '0018_payment_signature'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_method',
            field=models.CharField(max_length=50, null=True),
        ),
    ]