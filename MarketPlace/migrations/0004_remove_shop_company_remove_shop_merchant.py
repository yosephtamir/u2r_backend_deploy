# Generated by Django 5.0.3 on 2024-03-18 08:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("MarketPlace", "0003_remove_productcategory_thumbnail_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="shop",
            name="company",
        ),
        migrations.RemoveField(
            model_name="shop",
            name="merchant",
        ),
    ]
