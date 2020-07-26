from typing import List, Tuple

from celery import shared_task

from .api import DeviceAPI, WeatherAPI


@shared_task
def set_status(device_id: str, key: str, value):
    """ 设置设备参数 """
    if key is not None and value is not None:
        device_api = DeviceAPI(device_id)
        device_api.set_status(key, value)


@shared_task
def set_multiple_status(device_id: str, status: List[Tuple]):
    """ 设置设备参数

    status 为参数名和值的元组列表 [('valve1', True), ('valve2', True)]
    """
    if status is not None:
        device_api = DeviceAPI(device_id)
        device_api.set_multiple_status(status)


@shared_task
def autowatering(location_id: str, limit: float, device_id: str,
                 valves: List[str]):
    """ 根据当地的降雨情况自动浇水

    location_id: 中国天气网的地址 ID
    limit: 所需降雨量
    """
    need_water = False

    # 根据降水量判断是否需要浇水
    weather_api = WeatherAPI(location_id)
    rainfall = weather_api.rainfall_24h()
    if rainfall < limit:
        need_water = True

    if need_water:
        device_api = DeviceAPI(device_id)
        status = {valve: True for valve in valves}
        device_api.set_multiple_status(status)

    return f'{need_water=}, {rainfall=}'
