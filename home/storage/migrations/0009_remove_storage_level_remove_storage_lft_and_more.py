# Generated by Django 4.0.7 on 2022-09-29 12:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("storage", "0008_change_price_to_float"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="storage",
            name="level",
        ),
        migrations.RemoveField(
            model_name="storage",
            name="lft",
        ),
        migrations.RemoveField(
            model_name="storage",
            name="rght",
        ),
        migrations.RemoveField(
            model_name="storage",
            name="tree_id",
        ),
        migrations.AlterField(
            model_name="storage",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="children",
                to="storage.storage",
                verbose_name="属于",
            ),
        ),
    ]
