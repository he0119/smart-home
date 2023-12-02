# Generated by Django 3.2.9 on 2021-11-11 16:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("iot", "0006_do_not_allow_null"),
    ]

    operations = [
        migrations.CreateModel(
            name="AutowateringDataDaily",
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
                ("time", models.DateField(verbose_name="时间")),
                ("min_temperature", models.FloatField(verbose_name="最低温度")),
                ("max_temperature", models.FloatField(verbose_name="最高温度")),
                ("min_humidity", models.FloatField(verbose_name="最低湿度")),
                ("max_humidity", models.FloatField(verbose_name="最高湿度")),
                (
                    "min_wifi_signal",
                    models.IntegerField(verbose_name="最低无线信号强度"),
                ),
                (
                    "max_wifi_signal",
                    models.IntegerField(verbose_name="最高无线信号强度"),
                ),
                (
                    "device",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="data_daily",
                        to="iot.device",
                        verbose_name="设备",
                    ),
                ),
            ],
            options={
                "verbose_name": "自动浇水设备每日数据",
                "verbose_name_plural": "自动浇水设备每日数据",
            },
        ),
        migrations.AddIndex(
            model_name="autowateringdatadaily",
            index=models.Index(fields=["-time"], name="iot_autowat_time_fff2f5_idx"),
        ),
    ]
