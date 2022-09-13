import json
import os
from datetime import date, timedelta
from typing import cast
from unittest import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from requests import sessions
from strawberry_django_plus.gql import relay

from home.utils import GraphQLTestCase

from . import types
from .api import DeviceAPI, WeatherAPI
from .models import AutowateringData, AutowateringDataDaily, Device
from .tasks import (
    autowatering,
    clean_autowatering_database,
    set_multiple_status,
    set_status,
)


class ModelTests(TestCase):
    fixtures = ["users", "iot"]

    def test_device_str(self):
        device = Device.objects.get(name="test")

        self.assertEqual(str(device), "test")

    def test_autowateringdata_str(self):
        data = AutowateringData.objects.get(pk=1)

        self.assertEqual(str(data), f"test 2020-08-02T13:40:35+00:00")

    def test_autowateringdata_daily_str(self):
        data = AutowateringDataDaily.objects.get(pk=1)

        self.assertEqual(str(data), f"test 2020-01-01")


class DeviceTests(GraphQLTestCase):
    fixtures = ["users", "iot"]

    def setUp(self):
        self.user = get_user_model().objects.get(username="test")
        self.client.authenticate(self.user)

    def test_get_device(self):
        """获得指定设备信息"""
        test_device = Device.objects.get(name="test")

        query = """
            query device($id: GlobalID!) {
                device(id: $id) {
                    id
                    name
                    deviceType
                    location
                    autowateringData(filters: {}, order: {}) {
                        edges {
                            node {
                            id
                            temperature
                            }
                        }
                    }
                }
            }
        """
        variables = {
            "id": relay.to_base64(types.Device, test_device.id),
        }

        content = self.client.execute(query, variables)

        device = content.data["device"]
        self.assertEqual(device["name"], test_device.name)
        self.assertEqual(device["deviceType"], test_device.device_type)
        self.assertEqual(device["location"], test_device.location)
        data = [
            item["node"]["temperature"] for item in device["autowateringData"]["edges"]
        ]
        self.assertEqual(set(data), {1.0, 2.0, 3.0})

    def test_get_devices(self):
        """获取所有设备信息"""
        query = """
            query devices {
                devices {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
        """
        content = self.client.execute(query)

        names = [item["node"]["name"] for item in content.data["devices"]["edges"]]
        self.assertEqual(set(names), {"test", "test2"})

    def test_get_first_devices(self):
        """获取第一个设备的信息"""
        query = """
            query devices {
                devices(first: 1) {
                    edges {
                        node {
                            id
                            name
                            deviceType
                            autowateringData {
                                edges {
                                    node {
                                        id
                                        temperature
                                    }
                                }
                            }
                        }
                    }
                }
            }
        """
        content = self.client.execute(query)

        names = [item["node"]["name"] for item in content.data["devices"]["edges"]]
        self.assertEqual(set(names), {"test"})

    def test_add_device(self):
        """测试添加设备"""
        mutation = """
            mutation addDevice($input: AddDeviceInput!) {
                addDevice(input: $input) {
                    ... on Device {
                        __typename
                        id
                        name
                        deviceType
                        location
                        password
                    }
                }
            }
        """
        variables = {
            "input": {
                "name": "test2",
                "deviceType": "sometype",
                "location": "somelocation",
                "password": "public",
            }
        }

        content = self.client.execute(mutation, variables)

        device = content.data["addDevice"]
        self.assertEqual(device["__typename"], "Device")
        self.assertEqual(device["name"], "test2")
        self.assertEqual(device["deviceType"], "sometype")
        self.assertEqual(device["location"], "somelocation")
        self.assertEqual(
            device["password"],
            "efa1f375d76194fa51a3556a97e641e61685f914d446979da50a551a4333ffd7",
        )

    def test_delete_device(self):
        """测试删除设备"""
        mutation = """
            mutation deleteDevice($input: DeleteDeviceInput!) {
                deleteDevice(input: $input) {
                    __typename
                }
            }
        """

        test_device = Device.objects.get(name="test")
        variables = {
            "input": {"deviceId": relay.to_base64(types.Device, test_device.id)}
        }

        # 确认自动浇水有数据
        self.assertNotEqual(list(AutowateringData.objects.all()), [])

        content = self.client.execute(mutation, variables)

        with self.assertRaises(Device.DoesNotExist):
            Device.objects.get(name="test")
        # 确认是否同时删除自动浇水数据
        self.assertEqual(list(AutowateringData.objects.all()), [])

    def test_delete_device_not_exist(self):
        """测试删除不存在的设备"""
        mutation = """
            mutation deleteDevice($input: DeleteDeviceInput!) {
                deleteDevice(input: $input) {
                    ... on OperationInfo {
                        __typename
                        messages {
                            message
                        }
                    }
                }
            }
        """
        variables = {"input": {"deviceId": relay.to_base64(types.Device, "0")}}

        content = self.client.execute(mutation, variables)

        data = content.data["deleteDevice"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "设备不存在")

    def test_update_device(self):
        """测试更新设备"""
        mutation = """
            mutation updateDevice($input: UpdateDeviceInput!) {
                updateDevice(input: $input) {
                    ... on Device {
                        __typename
                        id
                        name
                        deviceType
                        location
                        password
                    }
                }
            }
        """
        variables = {
            "input": {
                "id": relay.to_base64(types.Device, "1"),
                "name": "newtest",
                "deviceType": "newdevicetype",
                "location": "newlocation",
                "password": "mqtt",
            }
        }

        old_Device = Device.objects.get(pk=1)
        self.assertEqual(old_Device.name, "test")

        content = self.client.execute(mutation, variables)

        device = content.data["updateDevice"]
        self.assertEqual(device["__typename"], "Device")
        self.assertEqual(device["id"], relay.to_base64(types.Device, "1"))
        self.assertEqual(device["name"], "newtest")
        self.assertEqual(device["deviceType"], "newdevicetype")
        self.assertEqual(device["location"], "newlocation")
        self.assertEqual(
            device["password"],
            "046adb88a188465c6ba56443392821e60e97d3806445ba0e9daea6fb7a94271e",
        )

    def test_update_device_not_exist(self):
        """测试更新不存在的设备"""
        mutation = """
            mutation updateDevice($input: UpdateDeviceInput!) {
                updateDevice(input: $input) {
                    ... on OperationInfo {
                        __typename
                        messages {
                            message
                        }
                    }
                }
            }
        """
        variables = {
            "input": {
                "id": relay.to_base64(types.Device, "0"),
                "name": "newtest",
                "deviceType": "newdevicetype",
                "location": "newlocation",
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["updateDevice"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "设备不存在")

    def test_set_device(self):
        """测试设置设备状态"""
        mutation = """
            mutation setDevice($input: SetDeviceInput!) {
                setDevice(input: $input) {
                    ... on Device {
                        __typename
                        id
                    }
                }
            }
        """
        variables = {
            "input": {
                "id": relay.to_base64(types.Device, "1"),
                "key": "valve1",
                "value": "1",
                "valueType": "bool",
            }
        }

        for value_type in ["bool", "float", "int", "str"]:
            variables["input"]["valueType"] = value_type

            content = self.client.execute(mutation, variables)

            device = content.data["setDevice"]
            self.assertEqual(device["__typename"], "Device")
            self.assertEqual(device["id"], relay.to_base64(types.Device, "1"))

    def test_set_device_not_exist(self):
        """测试设置不存在设备的状态"""
        mutation = """
            mutation setDevice($input: SetDeviceInput!) {
                setDevice(input: $input) {
                    ... on OperationInfo {
                        __typename
                        messages {
                            message
                        }
                    }
                }
            }
        """
        variables = {
            "input": {
                "id": relay.to_base64(types.Device, "0"),
                "key": "valve1",
                "value": "1",
                "valueType": "bool",
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["setDevice"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "设备不存在")

    def test_get_all_autowatering_data(self):
        """获取自动浇水数据"""
        query = """
            query autowateringData {
                autowateringData {
                    edges {
                        node {
                            temperature
                        }
                    }
                }
            }
        """
        variables = {"deviceId": relay.to_base64(types.Device, "1")}

        content = self.client.execute(query, variables)

        data = [
            item["node"]["temperature"]
            for item in content.data["autowateringData"]["edges"]
        ]
        self.assertEqual(set(data), {1.0, 2.0, 3.0})

    def test_get_first_autowatering_data(self):
        """获取指定数量的自动浇水数据"""
        query = """
            query autowateringData {
                autowateringData(first: 1) {
                    edges {
                        node {
                            temperature
                        }
                    }
                }
            }
        """
        content = self.client.execute(query)

        data = [
            item["node"]["temperature"]
            for item in content.data["autowateringData"]["edges"]
        ]
        self.assertEqual(set(data), {1.0})


class WebHookTests(TestCase):
    fixtures = ["users", "iot"]

    def test_webhook_get(self):
        """测试上报地址是否正常运行"""
        response = self.client.get(reverse("iot:iot"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"iot": "working"})

    def test_unknown_event(self):
        """测试未知的事件"""
        webhook_data = {
            "username": "admin",
            "proto_ver": 4,
            "keepalive": 15,
            "ipaddress": "221.10.55.132",
            "connected_at": 1607658682703,
            "clientid": "1",
            "action": "unknown",
        }
        response = self.client.post(
            reverse("iot:iot"),
            data=json.dumps(webhook_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

    def test_client_connected(self):
        """测试客户端连接"""
        webhook_data = {
            "username": "test",
            "proto_ver": 4,
            "keepalive": 15,
            "ipaddress": "221.10.55.132",
            "connected_at": 1607658682703,
            "clientid": "test",
            "action": "client_connected",
        }
        response = self.client.post(
            reverse("iot:iot"),
            data=json.dumps(webhook_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        device = Device.objects.get(name="test")
        self.assertEqual(device.is_online, True)

    def test_client_connected_not_exist(self):
        """测试客户端连接，但设备不存在"""
        webhook_data = {
            "username": "test0",
            "proto_ver": 4,
            "keepalive": 15,
            "ipaddress": "221.10.55.132",
            "connected_at": 1607658682703,
            "clientid": "test0",
            "action": "client_connected",
        }
        response = self.client.post(
            reverse("iot:iot"),
            data=json.dumps(webhook_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"iot": "working"})

    def test_client_disconnected(self):
        """测试客户端断开连接"""
        webhook_data = {
            "username": "test",
            "reason": "keepalive_timeout",
            "clientid": "test",
            "action": "client_disconnected",
        }
        response = self.client.post(
            reverse("iot:iot"),
            data=json.dumps(webhook_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        device = Device.objects.get(name="test")
        self.assertEqual(device.is_online, False)

    def test_client_disconnected_not_exist(self):
        """测试客户端断开连接，但设备不存在"""
        webhook_data = {
            "username": "test0",
            "reason": "keepalive_timeout",
            "clientid": "test0",
            "action": "client_disconnected",
        }
        response = self.client.post(
            reverse("iot:iot"),
            data=json.dumps(webhook_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"iot": "working"})

    def test_message_publish(self):
        """测试上报数据"""
        webhook_data = {
            "ts": 1607658685693,
            "topic": "device/test/status",
            "retain": False,
            "qos": 0,
            "payload": '{"timestamp":1607658685,"data":{"temperature":4.0,"humidity":0,"valve1":false,"valve2":false,"valve3":false,"pump":false,"valve1_delay":60,"valve2_delay":60,"valve3_delay":60,"pump_delay":60,"wifi_signal":-43}}',
            "from_username": "test",
            "from_client_id": "test",
            "action": "message_publish",
        }
        response = self.client.post(
            reverse("iot:iot"),
            data=json.dumps(webhook_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        autowatering_data = AutowateringData.objects.last()
        autowatering_data = cast(AutowateringData, autowatering_data)
        self.assertEqual(autowatering_data.temperature, 4.0)
        self.assertEqual(autowatering_data.wifi_signal, -43)

    def test_message_publish_not_exist(self):
        """测试上报数据，但设备不存在"""
        webhook_data = {
            "ts": 1607658685693,
            "topic": "device/test0/status",
            "retain": False,
            "qos": 0,
            "payload": '{"timestamp":1607658685,"data":{"temperature":4.0,"humidity":0,"valve1":false,"valve2":false,"valve3":false,"pump":false,"valve1_delay":60,"valve2_delay":60,"valve3_delay":60,"pump_delay":60,"wifi_signal":-43}}',
            "from_username": "test0",
            "from_client_id": "test0",
            "action": "message_publish",
        }
        response = self.client.post(
            reverse("iot:iot"),
            data=json.dumps(webhook_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        autowatering_data = AutowateringData.objects.last()
        autowatering_data = cast(AutowateringData, autowatering_data)
        self.assertEqual(autowatering_data.pk, 3)
        self.assertEqual(response.json(), {"iot": "working"})


def mocked_requests_get(*args, **kwargs):
    """天气信息的测试数据"""

    class MockResponse:
        def __init__(self, text):
            self.text = text

    if args[0] == "http://forecast.weather.com.cn/town/weather1dn/101270102006.shtml":
        filepath = os.path.join(settings.BASE_DIR, "home/iot/mock/weather.shtml")
        with open(filepath, "r", encoding="utf8") as f:
            text = f.read()
        return MockResponse(text)
    if args[0] == "http://forecast.weather.com.cn/town/weather1dn/1.shtml":
        return MockResponse("error")


def mocked_session_post(*args, **kwargs):
    """天气信息的测试数据"""

    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if (
        args[0]
        == f"http://{settings.EMQX_HTTP_HOST}:{settings.EMQX_HTTP_PORT}/api/v4/mqtt/publish"
    ):
        json = kwargs["json"]
        return MockResponse(
            json_data={
                "topic": json["topic"],
                "clientid": json["clientid"],
                "payload": json["payload"],
                "qos": json["qos"],
            },
            status_code=200,
        )


class ApiTests(TestCase):
    """测试 API"""

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_get_rainfall(self, mock_get):
        api = WeatherAPI("101270102006")
        rainfall = api.rainfall_24h()
        self.assertEqual(rainfall, 1)

        self.assertIn(
            mock.call(
                "http://forecast.weather.com.cn/town/weather1dn/101270102006.shtml"
            ),
            mock_get.call_args_list,
        )

    @mock.patch.object(sessions.Session, "post", side_effect=mocked_session_post)
    def test_set_status(self, mock_post):
        device = DeviceAPI("1")
        r = device.set_status("valve1", True)

        self.assertEqual(
            r,
            {
                "topic": "device/1/set",
                "clientid": "server",
                "payload": '{"valve1": true}',
                "qos": 1,
            },
        )

    @mock.patch.object(sessions.Session, "post", side_effect=mocked_session_post)
    def test_set_multiple_status(self, mock_post):
        device = DeviceAPI("1")
        r = device.set_multiple_status([("valve1", True), ("valve2", False)])

        self.assertEqual(
            r,
            {
                "topic": "device/1/set",
                "clientid": "server",
                "payload": '{"valve1": true, "valve2": false}',
                "qos": 1,
            },
        )


class TaskTests(TestCase):
    fixtures = ["users", "push"]

    @mock.patch.object(sessions.Session, "post", side_effect=mocked_session_post)
    def test_set_status(self, mock_post):
        set_status("1", "valve1", True)

        self.assertIn(
            mock.call(
                f"http://{settings.EMQX_HTTP_HOST}:{settings.EMQX_HTTP_PORT}/api/v4/mqtt/publish",
                json={
                    "topic": "device/1/set",
                    "clientid": "server",
                    "payload": '{"valve1": true}',
                    "qos": 1,
                },
            ),
            mock_post.call_args_list,
        )

    @mock.patch.object(sessions.Session, "post", side_effect=mocked_session_post)
    def test_set_multiple_status(self, mock_post):
        set_multiple_status("1", [("valve1", True), ("valve2", False)])

        self.assertIn(
            mock.call(
                f"http://{settings.EMQX_HTTP_HOST}:{settings.EMQX_HTTP_PORT}/api/v4/mqtt/publish",
                json={
                    "topic": "device/1/set",
                    "clientid": "server",
                    "payload": '{"valve1": true, "valve2": false}',
                    "qos": 1,
                },
            ),
            mock_post.call_args_list,
        )

    @mock.patch.object(sessions.Session, "post", side_effect=mocked_session_post)
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_autowatering(self, mock_get, mock_post):
        """测试自动浇水"""
        autowatering("101270102006", 10, "1", ["valve1"])

        self.assertIn(
            mock.call(
                "http://forecast.weather.com.cn/town/weather1dn/101270102006.shtml"
            ),
            mock_get.call_args_list,
        )
        self.assertIn(
            mock.call(
                f"http://{settings.EMQX_HTTP_HOST}:{settings.EMQX_HTTP_PORT}/api/v4/mqtt/publish",
                json={
                    "topic": "device/1/set",
                    "clientid": "server",
                    "payload": '{"valve1": true}',
                    "qos": 1,
                },
            ),
            mock_post.call_args_list,
        )

    @mock.patch.object(sessions.Session, "post", side_effect=mocked_session_post)
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_autowatering_do_not_need_water(self, mock_get, mock_post):
        """测试不需要浇水的情况"""
        autowatering("101270102006", 0, "1", ["valve1"])

        self.assertIn(
            mock.call(
                "http://forecast.weather.com.cn/town/weather1dn/101270102006.shtml"
            ),
            mock_get.call_args_list,
        )
        self.assertEqual(mock_post.call_args_list, [])

    @mock.patch.object(sessions.Session, "post", side_effect=mocked_session_post)
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_autowatering_with_error(self, mock_get, mock_post):
        """测试自动重试"""
        with self.assertRaises(TypeError):
            autowatering("1", 0, "1", ["valve1"])

        self.assertIn(
            mock.call("http://forecast.weather.com.cn/town/weather1dn/1.shtml"),
            mock_get.call_args_list,
        )
        self.assertEqual(mock_post.call_args_list, [])


class CleanDatabaseTests(TestCase):
    fixtures = ["users", "iot"]

    def test_empty_database(self):
        """测试数据库为空的情况"""
        # 删除所有数据
        AutowateringData.objects.all().delete()
        self.assertEqual(AutowateringData.objects.count(), 0)
        self.assertEqual(AutowateringDataDaily.objects.count(), 1)
        clean_autowatering_database()
        self.assertEqual(AutowateringData.objects.count(), 0)
        self.assertEqual(AutowateringDataDaily.objects.count(), 1)

    def test_clean_autowatering_database(self):
        """测试清理自动浇水数据库"""
        self.assertEqual(AutowateringData.objects.count(), 3)
        self.assertEqual(AutowateringDataDaily.objects.count(), 1)
        clean_autowatering_database()
        self.assertEqual(AutowateringData.objects.count(), 0)
        self.assertEqual(AutowateringDataDaily.objects.count(), 2)
        daily_data = AutowateringDataDaily.objects.last()
        daily_data = cast(AutowateringDataDaily, daily_data)
        self.assertEqual(daily_data.time, date(2020, 8, 2))
        self.assertEqual(daily_data.min_temperature, 1.0)
        self.assertEqual(daily_data.max_temperature, 3.0)
        self.assertEqual(daily_data.min_humidity, 0)
        self.assertEqual(daily_data.max_humidity, 0)
        self.assertEqual(daily_data.min_wifi_signal, -60)
        self.assertEqual(daily_data.max_wifi_signal, -59)

    def test_clean_autowatering_database_keep_30day(self):
        """测试清理自动浇水数据库是否是清理的 30 天的数据"""
        # 先删除所有
        AutowateringData.objects.all().delete()
        # 重新添加数据
        device = Device.objects.get(id=1)
        now = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        AutowateringData.objects.bulk_create(
            [
                AutowateringData(
                    device=device,
                    time=now - timedelta(days=29) + timedelta(seconds=1),
                    temperature=0.0,
                    humidity=0,
                    wifi_signal=0,
                    valve1=False,
                    valve2=False,
                    valve3=False,
                    pump=False,
                    valve1_delay=30,
                    valve2_delay=30,
                    valve3_delay=30,
                    pump_delay=30,
                ),
                AutowateringData(
                    device=device,
                    time=now - timedelta(days=30) + timedelta(seconds=1),
                    temperature=1.0,
                    humidity=0,
                    wifi_signal=-10,
                    valve1=False,
                    valve2=False,
                    valve3=False,
                    pump=False,
                    valve1_delay=30,
                    valve2_delay=30,
                    valve3_delay=30,
                    pump_delay=30,
                ),
                AutowateringData(
                    device=device,
                    time=now - timedelta(days=30) + timedelta(seconds=2),
                    temperature=2.0,
                    humidity=10,
                    wifi_signal=-20,
                    valve1=False,
                    valve2=False,
                    valve3=False,
                    pump=False,
                    valve1_delay=30,
                    valve2_delay=30,
                    valve3_delay=30,
                    pump_delay=30,
                ),
                AutowateringData(
                    device=device,
                    time=now - timedelta(days=30) + timedelta(seconds=3),
                    temperature=3.0,
                    humidity=20,
                    wifi_signal=-30,
                    valve1=False,
                    valve2=False,
                    valve3=False,
                    pump=False,
                    valve1_delay=30,
                    valve2_delay=30,
                    valve3_delay=30,
                    pump_delay=30,
                ),
            ]
        )
        # 处理数据
        self.assertEqual(AutowateringData.objects.count(), 4)
        self.assertEqual(AutowateringDataDaily.objects.count(), 1)
        clean_autowatering_database()
        self.assertEqual(AutowateringData.objects.count(), 1)
        self.assertEqual(AutowateringDataDaily.objects.count(), 2)
        daily_data = AutowateringDataDaily.objects.last()
        daily_data = cast(AutowateringDataDaily, daily_data)
        self.assertEqual(daily_data.time, now.date() - timedelta(days=30))
        self.assertEqual(daily_data.min_temperature, 1.0)
        self.assertEqual(daily_data.max_temperature, 3.0)
        self.assertEqual(daily_data.min_humidity, 0)
        self.assertEqual(daily_data.max_humidity, 20.0)
        self.assertEqual(daily_data.min_wifi_signal, -30)
        self.assertEqual(daily_data.max_wifi_signal, -10)
