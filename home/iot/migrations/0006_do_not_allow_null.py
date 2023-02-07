# Generated by Django 3.1.4 on 2021-01-24 09:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("iot", "0005_mqtt_auth"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mqttacl",
            name="clientid",
            field=models.CharField(
                blank=True, default="", max_length=100, verbose_name="客户端 ID"
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="mqttacl",
            name="ipaddr",
            field=models.CharField(
                blank=True, default="", max_length=60, verbose_name="IP 地址"
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="mqttacl",
            name="username",
            field=models.CharField(
                blank=True, default="", max_length=100, verbose_name="用户名"
            ),
            preserve_default=False,
        ),
    ]
