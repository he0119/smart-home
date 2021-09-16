import json
import re
from typing import Dict, List, Optional, Tuple

import requests
from django.conf import settings


class MQTTClient:
    def __init__(self) -> None:
        self.base_url = (
            f"http://{settings.EMQX_HTTP_HOST}:{settings.EMQX_HTTP_PORT}/api/v4/"
        )
        self.s = requests.Session()
        self.s.auth = (settings.EMQX_HTTP_APPID, settings.EMQX_HTTP_APPSECRET)

    def publish(self, topic: str, payload, qos: int) -> Dict:
        """发布消息"""
        data = {
            "topic": topic,
            "clientid": "server",
            "payload": json.dumps(payload),
            "qos": qos,
        }
        rjson = self.s.post(self.base_url + "mqtt/publish", json=data).json()
        return rjson


class DeviceAPI:
    def __init__(self, device_name: str) -> None:
        self.device_name = device_name
        self._client = MQTTClient()

    def set_status(self, key, value):
        """设置设备参数"""
        topic = f"device/{self.device_name}/set"
        payload = {key: value}
        r = self._client.publish(topic, payload, 1)
        return r

    def set_multiple_status(self, status: List[Tuple]):
        """设置设备的多个参数"""
        topic = f"device/{self.device_name}/set"
        payload = {key: value for key, value in status}
        r = self._client.publish(topic, payload, 1)
        return r


class WeatherAPI:
    """中国天气网

    http://www.weather.com.cn/
    """

    def __init__(self, location_id: str) -> None:
        self.location_id = location_id

    def weather_24h(self) -> Optional[List[Dict]]:
        """最近 24 小时的天气数据

        数据按时间降序排列
        od21 小时
        od22 温度(℃)
        od24 风向
        od25 风力
        od26 降水量(mm)
        od27 相对湿度
        """
        url = f"http://forecast.weather.com.cn/town/weather1dn/{self.location_id}.shtml"
        r = requests.get(url)
        r.encoding = "utf-8"
        match = re.findall(r"observe24h_data = ({.+});", r.text)
        for text in match:
            rjson = json.loads(text)
            if rjson["od"]["od0"] == self.location_id:
                return rjson["od"]["od2"]

    def rainfall_24h(self) -> float:
        """最近 24 小时的降雨量"""
        data = self.weather_24h()
        rainfall = 0
        for i in data:
            rainfall += i["od26"]
        return rainfall
