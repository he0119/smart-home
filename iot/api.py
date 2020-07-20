import json

import requests
from django.conf import settings


class MQTTClient:
    def __init__(self) -> None:
        self.base_url = f'http://{settings.EMQX_HTTP_HOST}:{settings.EMQX_HTTP_PORT}/api/v4/'
        self.s = requests.Session()
        self.s.auth = (settings.EMQX_HTTP_APPID, settings.EMQX_HTTP_APPSECRET)

    def get(self, url):
        return self.s.get(self.base_url + url).json()

    def post(self, url, data):
        return self.s.post(self.base_url + url, json=data).json()


class DeviceAPI:
    def __init__(self, device_id: str) -> None:
        self.device_id = device_id
        self._client = MQTTClient()

    def set_status(self, key, value):
        """ 设置设备参数 """
        data = {
            'topic': f'device/{self.device_id}/set',
            'clientid': 'server',
            'payload': json.dumps({key: value}),
            'qos': 1
        }
        r = self._client.post('mqtt/publish', data)
        return r
