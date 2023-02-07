# Generated by Django 3.0.8 on 2020-07-18 03:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("iot", "0002_auto_20200718_1154"),
    ]

    operations = [
        migrations.RenameField(
            model_name="device",
            old_name="date_created",
            new_name="created_at",
        ),
        migrations.RenameField(
            model_name="device",
            old_name="date_updated",
            new_name="edited_at",
        ),
        migrations.RenameField(
            model_name="device",
            old_name="date_online",
            new_name="online_at",
        ),
        migrations.RenameField(
            model_name="device",
            old_name="date_offline",
            new_name="offline_at",
        ),
        migrations.AlterField(
            model_name="device",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
        ),
        migrations.AlterField(
            model_name="device",
            name="edited_at",
            field=models.DateTimeField(auto_now=True, verbose_name="更新时间"),
        ),
        migrations.AlterField(
            model_name="device",
            name="offline_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="离线时间"),
        ),
        migrations.AlterField(
            model_name="device",
            name="online_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="在线时间"),
        ),
    ]
