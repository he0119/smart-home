import json
from typing import Dict, List, Tuple

import requests
from django.conf import settings


class MQTTClient:
    def __init__(self) -> None:
        self.base_url = f'http://{settings.EMQX_HTTP_HOST}:{settings.EMQX_HTTP_PORT}/api/v4/'
        self.s = requests.Session()
        self.s.auth = (settings.EMQX_HTTP_APPID, settings.EMQX_HTTP_APPSECRET)

    def publish(self, topic: str, payload, qos: int) -> Dict:
        """ 发布消息 """
        data = {
            'topic': topic,
            'clientid': 'server',
            'payload': json.dumps(payload),
            'qos': qos
        }
        rjson = self.s.post(self.base_url + 'mqtt/publish', json=data).json()
        return rjson


class DeviceAPI:
    def __init__(self, device_id: str) -> None:
        self.device_id = device_id
        self._client = MQTTClient()

    def set_status(self, key, value):
        """ 设置设备参数 """
        topic = f'device/{self.device_id}/set'
        payload = {key: value}
        r = self._client.publish(topic, payload, 1)
        return r

    def set_multiple_status(self, status: List[Tuple]):
        """ 设置设备的多个参数 """
        topic = f'device/{self.device_id}/set'
        payload = {key: value for key, value in status}
        r = self._client.publish(topic, payload, 1)
        return r
