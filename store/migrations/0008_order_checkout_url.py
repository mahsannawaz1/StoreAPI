# Generated by Django 4.1.4 on 2023-07-11 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_remove_order_total_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='checkout_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
