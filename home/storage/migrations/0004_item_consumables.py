# Generated by Django 3.1.4 on 2020-12-21 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("storage", "0003_logical_delete"),
    ]

    operations = [
        migrations.AddField(
            model_name="item",
            name="consumables",
            field=models.ManyToManyField(
                blank=True,
                related_name="consumed_by",
                to="storage.Item",
                verbose_name="耗材",
            ),
        ),
    ]
