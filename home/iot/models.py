from django.db import models
from django.utils.crypto import get_random_string


class Device(models.Model):
    """设备"""

    id = models.AutoField("ID", primary_key=True, auto_created=True)
    name = models.CharField("名字", max_length=100)
    device_type = models.CharField("类型", max_length=100)
    location = models.CharField("位置", max_length=100)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    edited_at = models.DateTimeField("更新时间", auto_now=True)
    is_online = models.BooleanField("在线状态")
    online_at = models.DateTimeField("在线时间", null=True, blank=True)
    offline_at = models.DateTimeField("离线时间", null=True, blank=True)
    token = models.CharField("令牌", max_length=100)

    class Meta:
        verbose_name = "设备"
        verbose_name_plural = "设备"

    def __str__(self):
        return self.name

    def generate_token(self):
        """生成令牌"""
        self.token = get_random_string(30)


class AutowateringData(models.Model):
    """自动浇水设备数据"""

    id = models.AutoField("ID", primary_key=True, auto_created=True)
    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name="data", verbose_name="设备"
    )
    time = models.DateTimeField("时间")
    temperature = models.FloatField("温度")
    humidity = models.FloatField("湿度")
    wifi_signal = models.IntegerField("无线信号强度")
    valve1 = models.BooleanField("阀门1")
    valve2 = models.BooleanField("阀门2")
    valve3 = models.BooleanField("阀门3")
    pump = models.BooleanField("水泵")
    valve1_delay = models.IntegerField("阀门1延迟")
    valve2_delay = models.IntegerField("阀门2延迟")
    valve3_delay = models.IntegerField("阀门3延迟")
    pump_delay = models.IntegerField("水泵延迟")

    class Meta:
        verbose_name = "自动浇水设备数据"
        verbose_name_plural = "自动浇水设备数据"
        indexes = [models.Index(fields=["-time"])]

    def __str__(self):
        return f"{self.device.name} {self.time.isoformat()}"


class AutowateringDataDaily(models.Model):
    """自动浇水设备每日数据"""

    id = models.AutoField("ID", primary_key=True, auto_created=True)
    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name="data_daily", verbose_name="设备"
    )
    time = models.DateField("时间")
    min_temperature = models.FloatField("最低温度")
    max_temperature = models.FloatField("最高温度")
    min_humidity = models.FloatField("最低湿度")
    max_humidity = models.FloatField("最高湿度")
    min_wifi_signal = models.IntegerField("最低无线信号强度")
    max_wifi_signal = models.IntegerField("最高无线信号强度")

    class Meta:
        verbose_name = "自动浇水设备每日数据"
        verbose_name_plural = "自动浇水设备每日数据"
        indexes = [models.Index(fields=["-time"])]

    def __str__(self):
        return f"{self.device.name} {self.time.isoformat()}"
