# Generated by Django 5.0.4 on 2024-05-08 14:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("Accounts", "0007_rename_managercountry_userprofile_usercountry_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="customuser",
            name="is_shopAdmin",
        ),
    ]
