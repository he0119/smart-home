# Generated by Django 3.0.8 on 2020-07-18 03:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='名字')),
                ('device_type', models.CharField(max_length=100, verbose_name='类型')),
                ('location', models.CharField(max_length=100, verbose_name='位置')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='创建日期')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='更新日期')),
                ('is_online', models.BooleanField(verbose_name='在线状态')),
                ('date_online', models.DateTimeField(verbose_name='上线日期')),
                ('date_offline', models.DateTimeField(blank=True, null=True, verbose_name='离线日期')),
            ],
            options={
                'verbose_name': '设备',
                'verbose_name_plural': '设备',
            },
        ),
        migrations.CreateModel(
            name='AutowateringData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(verbose_name='时间')),
                ('temperature', models.FloatField(verbose_name='温度')),
                ('humidity', models.FloatField(verbose_name='湿度')),
                ('wifi_signal', models.IntegerField(verbose_name='无线信号强度')),
                ('valve1', models.BooleanField(verbose_name='阀门1')),
                ('valve2', models.BooleanField(verbose_name='阀门2')),
                ('valve3', models.BooleanField(verbose_name='阀门3')),
                ('pump', models.BooleanField(verbose_name='水泵')),
                ('valve1_delay', models.IntegerField(verbose_name='阀门1延迟')),
                ('valve2_delay', models.IntegerField(verbose_name='阀门2延迟')),
                ('valve3_delay', models.IntegerField(verbose_name='阀门3延迟')),
                ('pump_delay', models.IntegerField(verbose_name='水泵延迟')),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data', to='iot.Device', verbose_name='设备')),
            ],
            options={
                'verbose_name': '自动浇水',
                'verbose_name_plural': '自动浇水',
            },
        ),
    ]
