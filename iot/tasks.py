from celery import shared_task

from .api import DeviceAPI


@shared_task
def set_status(device_id, key, value):
    """ 设置设备参数 """
    if key and value:
        device_api = DeviceAPI(device_id)
        device_api.set_status(key, value)
