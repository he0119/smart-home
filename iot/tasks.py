from typing import List, Tuple

from celery import shared_task

from .api import DeviceAPI


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
