from django.db import models


class Device(models.Model):
    """ 设备 """
    class Meta:
        verbose_name = '设备'
        verbose_name_plural = '设备'

    name = models.CharField(max_length=100, verbose_name='名字')
    device_type = models.CharField(max_length=100, verbose_name='类型')
    location = models.CharField(max_length=100, verbose_name='位置')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    edited_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_online = models.BooleanField(verbose_name='在线状态')
    online_at = models.DateTimeField(null=True,
                                     blank=True,
                                     verbose_name='在线时间')
    offline_at = models.DateTimeField(null=True,
                                      blank=True,
                                      verbose_name='离线时间')

    def __str__(self):
        return self.name


class AutowateringData(models.Model):
    """ 自动浇水设备数据 """
    class Meta:
        verbose_name = '自动浇水设备数据'
        verbose_name_plural = '自动浇水设备数据'
        indexes = [models.Index(fields=['-time'])]

    device = models.ForeignKey(Device,
                               on_delete=models.CASCADE,
                               related_name='data',
                               verbose_name='设备')
    time = models.DateTimeField(verbose_name='时间')
    temperature = models.FloatField(verbose_name='温度')
    humidity = models.FloatField(verbose_name='湿度')
    wifi_signal = models.IntegerField(verbose_name='无线信号强度')
    valve1 = models.BooleanField(verbose_name='阀门1')
    valve2 = models.BooleanField(verbose_name='阀门2')
    valve3 = models.BooleanField(verbose_name='阀门3')
    pump = models.BooleanField(verbose_name='水泵')
    valve1_delay = models.IntegerField(verbose_name='阀门1延迟')
    valve2_delay = models.IntegerField(verbose_name='阀门2延迟')
    valve3_delay = models.IntegerField(verbose_name='阀门3延迟')
    pump_delay = models.IntegerField(verbose_name='水泵延迟')

    def __str__(self):
        return f'{self.device.name} {self.time.isoformat()}'


class MQTTUser(models.Model):
    class Meta:
        verbose_name = 'MQTT 用户'
        verbose_name_plural = 'MQTT 用户'
        db_table = 'mqtt_user'

    device = models.OneToOneField(Device,
                                  on_delete=models.CASCADE,
                                  related_name='auth',
                                  verbose_name='设备')
    password = models.CharField(max_length=100, verbose_name='密码')
    salt = models.CharField(max_length=40,
                            null=True,
                            blank=True,
                            verbose_name='盐')


class MQTTAcl(models.Model):
    class Meta:
        verbose_name = 'ACL 规则'
        verbose_name_plural = 'ACL 规则'
        db_table = 'mqtt_acl'

    allow = models.IntegerField(verbose_name='允许')
    ipaddr = models.CharField(max_length=60,
                              null=True,
                              blank=True,
                              verbose_name='IP 地址')
    username = models.CharField(max_length=100,
                                null=True,
                                blank=True,
                                verbose_name='用户名')
    clientid = models.CharField(max_length=100,
                                null=True,
                                blank=True,
                                verbose_name='客户端 ID')
    access = models.IntegerField(verbose_name='操作')
    topic = models.CharField(max_length=100, verbose_name='主题')
