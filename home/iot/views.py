import json
import logging
from datetime import datetime

import pytz
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import AutowateringData, Device

logger = logging.getLogger('iot')


@csrf_exempt
def iot(request):
    """ 物联网

    EMQX WebHook
    """
    if request.method == 'POST':
        event = json.loads(request.body)
        logger.debug(event)
        if event['action'] == 'message_publish':
            process_message_publish(event)
        elif event['action'] == 'client_connected':
            process_client_connected(event)
        elif event['action'] == 'client_disconnected':
            process_client_disconnected(event)
        else:
            logger.warning('未处理的事件')
            logger.warning(event)

    return JsonResponse({'iot': 'working'})


def process_message_publish(event):
    """ 处理消息发布事件 """
    device_name = event['from_username']
    topic = event['topic']
    if 'status' in topic:
        payload = json.loads(event['payload'])
        try:
            device = Device.objects.get(name=device_name)
            if device.device_type == 'autowatering':
                autowatering_data = AutowateringData(
                    device=device,
                    time=datetime.fromtimestamp(payload['timestamp'],
                                                pytz.utc),
                    temperature=payload['data']['temperature'],
                    humidity=payload['data']['humidity'],
                    wifi_signal=payload['data']['wifi_signal'],
                    valve1=payload['data']['valve1'],
                    valve2=payload['data']['valve2'],
                    valve3=payload['data']['valve3'],
                    pump=payload['data']['pump'],
                    valve1_delay=payload['data']['valve1_delay'],
                    valve2_delay=payload['data']['valve2_delay'],
                    valve3_delay=payload['data']['valve3_delay'],
                    pump_delay=payload['data']['pump_delay'],
                )
                autowatering_data.save()
                logger.debug(f'{device.name} {autowatering_data.time} 保存成功')
        except Device.DoesNotExist:
            logger.error(f'设备({device_name}) 不存在')


def process_client_disconnected(event):
    """ 处理设备下线事件 """
    device_name = event['username']
    try:
        device = Device.objects.get(name=device_name)
        device.is_online = False
        device.offline_at = timezone.now()
        device.save()
        logger.info(f'{device.name} 离线')
    except Device.DoesNotExist:
        logger.error(f'设备({device_name}) 不存在')


def process_client_connected(event):
    """ 处理设备上线事件 """
    device_name = event['username']
    try:
        device = Device.objects.get(name=device_name)
        device.is_online = True
        device.online_at = timezone.now()
        device.save()
        logger.info(f'{device.name} 在线')
    except Device.DoesNotExist:
        logger.error(f'设备({device_name}) 不存在')
