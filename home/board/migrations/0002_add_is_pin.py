# Generated by Django 3.1.4 on 2020-12-23 10:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("board", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="topic",
            options={"verbose_name": "话题", "verbose_name_plural": "话题"},
        ),
        migrations.AddField(
            model_name="topic",
            name="is_pin",
            field=models.BooleanField(default=False, verbose_name="置顶"),
        ),
    ]
