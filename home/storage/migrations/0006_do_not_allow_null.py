# Generated by Django 3.1.4 on 2021-01-24 09:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("storage", "0005_edited_at_not_auto_now"),
    ]

    operations = [
        migrations.AlterField(
            model_name="item",
            name="description",
            field=models.CharField(
                blank=True, default="", max_length=200, verbose_name="备注"
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="storage",
            name="description",
            field=models.CharField(
                blank=True, default="", max_length=200, verbose_name="备注"
            ),
            preserve_default=False,
        ),
    ]
