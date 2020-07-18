import json
import logging
from datetime import datetime

from django.http import JsonResponse
from django.utils.timezone import make_aware
from django.views.decorators.csrf import csrf_exempt

from .models import AutowateringData, Device

logger = logging.getLogger('IOT')


@csrf_exempt
def iot(request):
    """ 物联网

    EMQX WebHook
    """
    if request.method == 'POST':
        try:
            event = json.loads(request.body)
            logger.info(event)
            if event['action'] == 'message_publish':
                process_message_publish(event)
            if event['action'] == 'client_connected':
                process_client_connected(event)
            if event['action'] == 'client_disconnected':
                process_client_disconnected(event)
        except:
            pass

    return JsonResponse({'iot': 'working'})


def process_message_publish(event):
    """ 处理消息发布 """
    topic = event['topic']
    if 'status' in topic:
        payload = json.loads(event['payload'])
        device_id = payload['device_id']
        try:
            device = Device.objects.get(pk=device_id)
            if device.device_type == 'autowatering':
                autowatering_data = AutowateringData(
                    device=device,
                    time=make_aware(
                        datetime.fromtimestamp(payload['timestamp'])),
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
                logger.info(f'{device.name} {autowatering_data.time} 保存成功')
        except Device.DoesNotExist:
            logger.error(f'设备 ID({device_id}) 不存在')
        except Exception as e:
            logger.error(e)


def process_client_disconnected(event):
    """ 设备下线 """
    device_id = event['clientid']
    try:
        device = Device.objects.get(pk=int(device_id))
        device.is_online = False
        device.date_offline = datetime.now()
        device.save()
        logger.info(f'{device.name} {device.date_offline} 已离线')
    except Device.DoesNotExist:
        logger.error(f'设备 ID({device_id}) 不存在')
    except Exception as e:
        logger.error(e)


def process_client_connected(event):
    """ 设备上线 """
    device_id = event['clientid']
    try:
        device = Device.objects.get(pk=int(device_id))
        device.is_online = True
        device.date_online = datetime.now()
        device.save()
        logger.info(f'{device.name} {device.date_online} 已上线')
    except Device.DoesNotExist:
        logger.error(f'设备 ID({device_id}) 不存在')
    except Exception as e:
        logger.error(e)
