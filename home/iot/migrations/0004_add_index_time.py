# Generated by Django 3.1.4 on 2020-12-28 05:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("iot", "0003_rename_field"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="autowateringdata",
            index=models.Index(fields=["-time"], name="iot_autowat_time_3b702b_idx"),
        ),
    ]
