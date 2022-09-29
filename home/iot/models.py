from django.db import models


class Device(models.Model):
    """设备"""

    class Meta:
        verbose_name = "设备"
        verbose_name_plural = "设备"

    name = models.CharField(max_length=100, verbose_name="名字")
    device_type = models.CharField(max_length=100, verbose_name="类型")
    location = models.CharField(max_length=100, verbose_name="位置")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    edited_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_online = models.BooleanField(verbose_name="在线状态")
    online_at = models.DateTimeField(null=True, blank=True, verbose_name="在线时间")
    offline_at = models.DateTimeField(null=True, blank=True, verbose_name="离线时间")
    password = models.CharField(max_length=100, verbose_name="密码")

    def __str__(self):
        return self.name


class AutowateringData(models.Model):
    """自动浇水设备数据"""

    class Meta:
        verbose_name = "自动浇水设备数据"
        verbose_name_plural = "自动浇水设备数据"
        indexes = [models.Index(fields=["-time"])]

    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name="data", verbose_name="设备"
    )
    time = models.DateTimeField(verbose_name="时间")
    temperature = models.FloatField(verbose_name="温度")
    humidity = models.FloatField(verbose_name="湿度")
    wifi_signal = models.IntegerField(verbose_name="无线信号强度")
    valve1 = models.BooleanField(verbose_name="阀门1")
    valve2 = models.BooleanField(verbose_name="阀门2")
    valve3 = models.BooleanField(verbose_name="阀门3")
    pump = models.BooleanField(verbose_name="水泵")
    valve1_delay = models.IntegerField(verbose_name="阀门1延迟")
    valve2_delay = models.IntegerField(verbose_name="阀门2延迟")
    valve3_delay = models.IntegerField(verbose_name="阀门3延迟")
    pump_delay = models.IntegerField(verbose_name="水泵延迟")

    def __str__(self):
        return f"{self.device.name} {self.time.isoformat()}"


class AutowateringDataDaily(models.Model):
    """自动浇水设备每日数据"""

    class Meta:
        verbose_name = "自动浇水设备每日数据"
        verbose_name_plural = "自动浇水设备每日数据"
        indexes = [models.Index(fields=["-time"])]

    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name="data_daily", verbose_name="设备"
    )
    time = models.DateField(verbose_name="时间")
    min_temperature = models.FloatField(verbose_name="最低温度")
    max_temperature = models.FloatField(verbose_name="最高温度")
    min_humidity = models.FloatField(verbose_name="最低湿度")
    max_humidity = models.FloatField(verbose_name="最高湿度")
    min_wifi_signal = models.IntegerField(verbose_name="最低无线信号强度")
    max_wifi_signal = models.IntegerField(verbose_name="最高无线信号强度")

    def __str__(self):
        return f"{self.device.name} {self.time.isoformat()}"
