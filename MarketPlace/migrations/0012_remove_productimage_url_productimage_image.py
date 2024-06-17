# Generated by Django 5.0.3 on 2024-04-10 15:33

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("MarketPlace", "0011_alter_product_status"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="productimage",
            name="url",
        ),
        migrations.AddField(
            model_name="productimage",
            name="image",
            field=cloudinary.models.CloudinaryField(
                blank=True, max_length=255, null=True
            ),
        ),
    ]
