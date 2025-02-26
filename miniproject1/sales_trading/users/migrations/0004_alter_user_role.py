# Generated by Django 5.1.6 on 2025-02-25 17:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0003_alter_user_role"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("admin", "Admin"),
                    ("trader", "Trader"),
                    ("sales", "Sales Representative"),
                    ("customer", "Customer"),
                ],
                default="customer",
                max_length=10,
            ),
        ),
    ]
