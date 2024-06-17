# Generated by Django 5.0.3 on 2024-04-10 12:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("MarketPlace", "0007_alter_product_has_discount_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="MarketPlace.productcategory",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="sub_category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="MarketPlace.productsubcategory",
            ),
        ),
    ]
