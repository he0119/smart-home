import json
import re
from typing import Any, Dict, List, Tuple

import requests

from home.utils import channel_group_send


class DeviceAPI:
    def __init__(self, device_id: str) -> None:
        self.device_id = device_id

    def set_status(self, key: str, value: Any):
        """设置设备参数"""
        payload = {key: value}
        channel_group_send(
            "iot",
            {"type": "set_device", "pk": self.device_id, "data": payload},
        )

    def set_multiple_status(self, status: List[Tuple]):
        """设置设备的多个参数"""
        payload = {key: value for key, value in status}
        channel_group_send(
            "iot",
            {"type": "set_device", "pk": self.device_id, "data": payload},
        )


class WeatherAPI:
    """中国天气网

    http://www.weather.com.cn/
    """

    def __init__(self, location_id: str) -> None:
        self.location_id = location_id

    def weather_24h(self) -> List[Dict]:
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

        raise Exception("无法获取到天气数据")

    def rainfall_24h(self) -> float:
        """最近 24 小时的降雨量"""
        data = self.weather_24h()
        rainfall = 0
        for i in data:
            rainfall += i["od26"]
        return rainfall
