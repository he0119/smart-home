# Generated by Django 4.1.4 on 2023-01-03 01:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("storage", "0008_change_price_to_float"),
    ]

    operations = [
        migrations.AlterField(
            model_name="item",
            name="name",
            field=models.CharField(max_length=200, verbose_name="名字"),
        ),
        migrations.AlterField(
            model_name="storage",
            name="name",
            field=models.CharField(max_length=200, verbose_name="名字"),
        ),
    ]
