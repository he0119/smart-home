# Generated by Django 3.1.7 on 2021-03-09 08:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import home.storage.models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("storage", "0006_do_not_allow_null"),
    ]

    operations = [
        migrations.CreateModel(
            name="Picture",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "description",
                    models.CharField(blank=True, max_length=200, verbose_name="备注"),
                ),
                (
                    "picture",
                    models.ImageField(upload_to=home.storage.models.get_file_path, verbose_name="图片"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="添加时间"),
                ),
                ("box_x", models.FloatField(verbose_name="边界框中心点 X")),
                ("box_y", models.FloatField(verbose_name="边界框中心点 Y")),
                ("box_h", models.FloatField(verbose_name="边界框高")),
                ("box_w", models.FloatField(verbose_name="边界框宽")),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="添加人",
                    ),
                ),
                (
                    "item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="pictures",
                        to="storage.item",
                        verbose_name="物品",
                    ),
                ),
            ],
            options={
                "verbose_name": "图片",
                "verbose_name_plural": "图片",
            },
        ),
    ]
