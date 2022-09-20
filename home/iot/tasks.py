from datetime import datetime, timedelta
from typing import List, Optional

from celery import shared_task
from django.db.models import Max, Min
from django.utils import timezone

from home.push.tasks import get_enable_reg_ids, push_to_users

from .api import DeviceAPI, WeatherAPI
from .models import AutowateringData, AutowateringDataDaily, Device


@shared_task(bind=True)
def autowatering(
    self, location_id: str, limit: float, device_id: str, valves: List[str]
) -> str:
    """根据当地的降雨情况自动浇水

    location_id: 中国天气网的地址 ID
    limit: 所需降雨量
    """
    need_water = False

    # 根据降水量判断是否需要浇水
    weather_api = WeatherAPI(location_id)
    try:
        rainfall = weather_api.rainfall_24h()
        if rainfall < limit:
            need_water = True
    except Exception as exc:
        raise self.retry(exc=exc)

    if need_water:
        device_api = DeviceAPI(device_id)
        status = [(valve, True) for valve in valves]
        device_api.set_multiple_status(status)
        push_message = f"今天的降雨量为 {rainfall:.1f}，已开启阀门"
    else:
        push_message = f"今天的降雨量为 {rainfall:.1f}，不需要浇水呢"

    # 向用户推送消息
    reg_ids = get_enable_reg_ids()
    if reg_ids:
        push_to_users.delay(
            reg_ids,
            "自动浇水",
            push_message,
            "/iot",
            True,
        )  # type: ignore
    return push_message


@shared_task
def clean_autowatering_database():
    """清理自动浇水的数据库

    删除一个月前的所有数据
    只保留最高和最低的两条数据
    """
    data = []

    # 今天零点作为最大值的范围就是前一天的最后了，所以 30 天前的数据，只需要减 29 天
    max_time = timezone.now().replace(
        hour=0, minute=0, second=0, microsecond=0
    ) - timedelta(days=29)

    for device in Device.objects.all():
        min_time: Optional[datetime] = device.data.aggregate(Min("time"))["time__min"]
        if not min_time:
            continue

        # 只处理一个月前的数据
        min_time = min_time.replace(hour=0, minute=0, second=0, microsecond=0)

        # 相差天数
        days = (max_time - min_time).days

        for i in range(days):
            # 每天的时间
            min_datetime = min_time + timedelta(days=i)
            max_datetime = min_time + timedelta(days=i + 1)
            all_day_data = device.data.filter(
                time__gte=min_datetime,
                time__lte=max_datetime,
            )

            # 如果这一天没有数据则跳过
            if all_day_data.count() == 0:
                continue

            # 获取最低温度和最高温度
            min_temperature = all_day_data.aggregate(Min("temperature"))[
                "temperature__min"
            ]
            max_temperature = all_day_data.aggregate(Max("temperature"))[
                "temperature__max"
            ]
            min_humidity = all_day_data.aggregate(Min("humidity"))["humidity__min"]
            max_humidity = all_day_data.aggregate(Max("humidity"))["humidity__max"]
            min_wifi_signal = all_day_data.aggregate(Min("wifi_signal"))[
                "wifi_signal__min"
            ]
            max_wifi_signal = all_day_data.aggregate(Max("wifi_signal"))[
                "wifi_signal__max"
            ]
            data.append(
                AutowateringDataDaily(
                    device=device,
                    time=min_datetime.date(),
                    min_temperature=min_temperature,
                    max_temperature=max_temperature,
                    min_humidity=min_humidity,
                    max_humidity=max_humidity,
                    min_wifi_signal=min_wifi_signal,
                    max_wifi_signal=max_wifi_signal,
                )
            )

    # 创建并删除数据
    AutowateringDataDaily.objects.bulk_create(data)
    AutowateringData.objects.filter(time__lt=max_time).delete()
