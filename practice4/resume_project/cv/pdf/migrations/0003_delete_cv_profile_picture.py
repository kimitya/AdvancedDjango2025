# Generated by Django 5.1.6 on 2025-02-12 16:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pdf", "0002_cv"),
    ]

    operations = [
        migrations.DeleteModel(
            name="CV",
        ),
        migrations.AddField(
            model_name="profile",
            name="picture",
            field=models.ImageField(
                blank=True, null=True, upload_to="profile_pictures/"
            ),
        ),
    ]
