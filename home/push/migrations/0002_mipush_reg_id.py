# Generated by Django 3.1.3 on 2020-11-27 15:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("push", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="mipush",
            name="reg_id",
            field=models.TextField(null=True, unique=True, verbose_name="注册标识码"),
        ),
    ]
