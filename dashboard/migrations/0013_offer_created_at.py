# Generated by Django 5.1.2 on 2024-10-31 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0012_remove_product_flat_discount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
