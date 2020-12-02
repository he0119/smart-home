from typing import List, Tuple

from celery import shared_task

from home.push.tasks import PushChannel, get_enable_reg_ids, push_to_users

from .api import DeviceAPI, WeatherAPI


@shared_task
def set_status(device_id: str, key: str, value) -> None:
    """ 设置设备参数 """
    if key is not None and value is not None:
        device_api = DeviceAPI(device_id)
        device_api.set_status(key, value)


@shared_task
def set_multiple_status(device_id: str, status: List[Tuple]) -> None:
    """ 设置设备参数

    status 为参数名和值的元组列表 [('valve1', True), ('valve2', True)]
    """
    if status is not None:
        device_api = DeviceAPI(device_id)
        device_api.set_multiple_status(status)


@shared_task(bind=True)
def autowatering(self, location_id: str, limit: float, device_id: str,
                 valves: List[str]) -> str:
    """ 根据当地的降雨情况自动浇水

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
        push_message = f'今天的降雨量为 {rainfall}，已开启阀门'
    else:
        push_message = f'今天的降雨量为 {rainfall}，不需要浇水呢'

    # 向用户推送消息
    reg_ids = get_enable_reg_ids()
    if reg_ids:
        push_to_users.delay(
            reg_ids,
            '自动浇水',
            push_message,
            PushChannel.IOT.value,
        )
    return f'{need_water=}, {rainfall=}'
