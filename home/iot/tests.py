import asyncio
import base64
import os
from datetime import date, timedelta
from typing import Optional, cast
from unittest import mock

from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import path
from django.utils import timezone
from strawberry.subscriptions import GRAPHQL_WS_PROTOCOL
from strawberry.subscriptions.protocols.graphql_ws import (
    GQL_CONNECTION_ACK,
    GQL_CONNECTION_INIT,
    GQL_DATA,
    GQL_START,
)
from strawberry_django_plus.gql import relay

from home.utils import GraphQLTestCase, get_ws_client

from . import types
from .api import DeviceAPI, WeatherAPI
from .models import AutowateringData, AutowateringDataDaily, Device
from .tasks import autowatering, clean_autowatering_database
from .views import BasicAuthMiddleware, IotConsumer


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
                        token
                    }
                }
            }
        """
        variables = {
            "input": {
                "name": "test2",
                "deviceType": "sometype",
                "location": "somelocation",
            }
        }

        content = self.client.execute(mutation, variables)

        device = content.data["addDevice"]
        self.assertEqual(device["__typename"], "Device")
        self.assertEqual(device["name"], "test2")
        self.assertEqual(device["deviceType"], "sometype")
        self.assertEqual(device["location"], "somelocation")
        self.assertEqual(len(device["token"]), 30)

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
                        token
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
        self.assertEqual(device["token"], "XS2iq6df48tULQVa7f6MbbHkq8wQpf")

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
                "valueType": "BOOLEAN",
            }
        }

        for value_type in ["BOOLEAN", "FLOAT", "INTEGER", "STRING"]:
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
                "valueType": "BOOLEAN",
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


def get_iot_client(device: Optional[Device] = None) -> WebsocketCommunicator:
    """获取物联网 WebSocket 客户端"""
    application = URLRouter(
        [
            path("iot/", BasicAuthMiddleware(IotConsumer.as_asgi())),
        ]
    )
    authorization = b""
    if device:
        authorization = base64.b64encode(f"{device.id}:{device.token}".encode())
    communicator = WebsocketCommunicator(
        application,
        "/iot/",
        headers=[
            (
                b"authorization",
                b"Basic " + authorization,
            )
        ],
    )

    return communicator


class WebSocketsTests(TestCase):
    fixtures = ["users", "iot"]

    def setUp(self) -> None:
        self.device = Device.objects.get(pk=1)

    async def test_client_connected_disconnected(self):
        """测试客户端连接"""
        communicator = get_iot_client(self.device)

        # 在线
        connected, subprotocol = await communicator.connect()
        assert connected

        device = await sync_to_async(Device.objects.get)(pk=1)
        self.assertEqual(device.is_online, True)

        # 离线
        await communicator.disconnect()

        device = await sync_to_async(Device.objects.get)(pk=1)
        self.assertEqual(device.is_online, False)

    async def test_client_connected_not_exist(self):
        """测试客户端连接，但设备不存在"""
        communicator = get_iot_client(Device(pk=0, token=""))

        connected, subprotocol = await communicator.connect()
        assert not connected

    async def test_client_connected_wrong_token(self):
        """测试客户端连接，但设备密码错误"""
        communicator = get_iot_client(Device(pk=1, token="123456"))

        connected, subprotocol = await communicator.connect()
        assert not connected

    async def test_client_connected_wrong_headers(self):
        """测试客户端连接，但 headers 错误"""
        communicator = get_iot_client()

        connected, subprotocol = await communicator.connect()
        assert not connected

    async def test_message_publish(self):
        """测试上报数据"""
        communicator = get_iot_client(self.device)

        # 在线
        connected, subprotocol = await communicator.connect()
        assert connected

        await communicator.send_json_to(
            {
                "id": 1607658685,
                "method": "properties_changed",
                "params": {
                    "temperature": 4.0,
                    "humidity": 0,
                    "valve1": False,
                    "valve2": False,
                    "valve3": False,
                    "pump": False,
                    "valve1_delay": 60,
                    "valve2_delay": 60,
                    "valve3_delay": 60,
                    "pump_delay": 60,
                    "wifi_signal": -43,
                },
            }
        )
        with self.assertRaises(asyncio.exceptions.TimeoutError):
            response = await communicator.receive_from(1)

        autowatering_data = await sync_to_async(AutowateringData.objects.last)()
        autowatering_data = cast(AutowateringData, autowatering_data)
        self.assertEqual(autowatering_data.temperature, 4.0)
        self.assertEqual(autowatering_data.wifi_signal, -43)

    async def test_set_device(self):
        """测试设置设备状态"""
        communicator = get_iot_client(self.device)

        # 在线
        connected, subprotocol = await communicator.connect()
        assert connected

        channel_layer = get_channel_layer()
        await channel_layer.group_send(  # type: ignore
            "iot", {"type": "set_device", "id": "1", "data": {"valve1": True}}
        )

        response = await communicator.receive_json_from()

        self.assertEqual(response["method"], "set_properties")
        self.assertEqual(response["params"], {"valve1": True})


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

    @mock.patch("home.iot.api.channel_group_send")
    def test_set_status(self, mock_send):
        device = DeviceAPI("1")
        r = device.set_status("valve1", True)

        mock_send.assert_called_once_with(
            "iot", {"type": "set_device", "id": "1", "data": {"valve1": True}}
        )

    @mock.patch("home.iot.api.channel_group_send")
    def test_set_multiple_status(self, mock_send):
        device = DeviceAPI("1")
        r = device.set_multiple_status([("valve1", True), ("valve2", False)])

        mock_send.assert_called_once_with(
            "iot",
            {
                "type": "set_device",
                "id": "1",
                "data": {"valve1": True, "valve2": False},
            },
        )


class TaskTests(TestCase):
    fixtures = ["users", "push"]

    @mock.patch("home.iot.api.channel_group_send")
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_autowatering(self, mock_get, mock_send):
        """测试自动浇水"""
        autowatering("101270102006", 10, "1", ["valve1"])

        mock_get.assert_called_once_with(
            "http://forecast.weather.com.cn/town/weather1dn/101270102006.shtml"
        )
        mock_send.assert_called_once_with(
            "iot", {"type": "set_device", "id": "1", "data": {"valve1": True}}
        )

    @mock.patch("home.iot.api.channel_group_send")
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_autowatering_do_not_need_water(self, mock_get, mock_send):
        """测试不需要浇水的情况"""
        autowatering("101270102006", 0, "1", ["valve1"])

        mock_get.assert_called_once_with(
            "http://forecast.weather.com.cn/town/weather1dn/101270102006.shtml"
        )
        mock_send.assert_not_called()

    @mock.patch("home.iot.api.channel_group_send")
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_autowatering_with_error(self, mock_get, mock_send):
        """测试自动重试"""
        with self.assertRaises(Exception):
            autowatering("1", 0, "1", ["valve1"])

        mock_get.assert_called_once_with(
            "http://forecast.weather.com.cn/town/weather1dn/1.shtml"
        )
        mock_send.assert_not_called()


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


class SubscriptionTests(TestCase):
    fixtures = ["users", "iot"]

    def setUp(self) -> None:
        self.user = get_user_model().objects.get(username="test")

    async def test_device(self):
        query = """
        subscription device($id: GlobalID!) {
            device(id: $id) {
                __typename
                id
                name
                location
              }
            }
        """
        variables = {"id": relay.to_base64(types.Device, 1)}
        ws = get_ws_client(self.user)
        res = await ws.connect()
        assert res == (True, GRAPHQL_WS_PROTOCOL)
        await ws.send_json_to({"type": GQL_CONNECTION_INIT})
        await ws.send_json_to(
            {
                "type": GQL_START,
                "id": "demo_consumer",
                "payload": {"query": f"{query}", "variables": variables},
            }
        )
        response = await ws.receive_json_from()
        assert response["type"] == GQL_CONNECTION_ACK

        response = await ws.receive_json_from()
        assert response["type"] == GQL_DATA
        assert response["id"] == "demo_consumer"
        data = response["payload"]["data"]["device"]
        assert data["id"] == relay.to_base64(types.Device, 1)
        assert data["name"] == "test"
        assert data["location"] == "location"

        channel_layer = get_channel_layer()
        await channel_layer.group_send("device.1", {"type": "update"})  # type: ignore

        response = await ws.receive_json_from()
        assert response["type"] == GQL_DATA
        assert response["id"] == "demo_consumer"
        data = response["payload"]["data"]["device"]
        assert data["id"] == relay.to_base64(types.Device, 1)
        assert data["name"] == "test"
        assert data["location"] == "location"

    async def test_device_not_exist(self):
        """测试订阅不存在的设备"""
        query = """
        subscription device($id: GlobalID!) {
            device(id: $id) {
                __typename
                id
                name
                location
              }
            }
        """
        variables = {"id": relay.to_base64(types.Device, 0)}
        ws = get_ws_client(self.user)
        res = await ws.connect()
        assert res == (True, GRAPHQL_WS_PROTOCOL)
        await ws.send_json_to({"type": GQL_CONNECTION_INIT})
        await ws.send_json_to(
            {
                "type": GQL_START,
                "id": "demo_consumer",
                "payload": {"query": f"{query}", "variables": variables},
            }
        )
        response = await ws.receive_json_from()
        assert response["type"] == GQL_CONNECTION_ACK

        response = await ws.receive_json_from()
        assert response["type"] == GQL_DATA
        assert response["id"] == "demo_consumer"
        assert response["payload"]["errors"][0]["message"] == "['设备不存在']"

    async def test_autowatering_data(self):
        query = """
        subscription autowatering_data($deviceId: GlobalID!) {
            autowateringData(deviceId: $deviceId) {
                __typename
                id
                time
              }
            }
        """
        variables = {"deviceId": relay.to_base64(types.Device, 1)}
        ws = get_ws_client(self.user)
        res = await ws.connect()
        assert res == (True, GRAPHQL_WS_PROTOCOL)
        await ws.send_json_to({"type": GQL_CONNECTION_INIT})
        await ws.send_json_to(
            {
                "type": GQL_START,
                "id": "demo_consumer",
                "payload": {"query": f"{query}", "variables": variables},
            }
        )
        response = await ws.receive_json_from()
        assert response["type"] == GQL_CONNECTION_ACK

        response = await ws.receive_json_from()
        assert response["type"] == GQL_DATA
        assert response["id"] == "demo_consumer"
        data = response["payload"]["data"]["autowateringData"]
        assert data["id"] == relay.to_base64(types.AutowateringData, 3)
        assert data["time"] == "2020-08-02T13:40:55+00:00"

        channel_layer = get_channel_layer()
        await channel_layer.group_send("autowatering_data.1", {"type": "update", "pk": 2})  # type: ignore

        response = await ws.receive_json_from()
        assert response["type"] == GQL_DATA
        assert response["id"] == "demo_consumer"
        data = response["payload"]["data"]["autowateringData"]
        assert data["id"] == relay.to_base64(types.AutowateringData, 2)
        assert data["time"] == "2020-08-02T13:40:45+00:00"

    async def test_autowatering_data_device_not_exist(self):
        """测试订阅不存在的设备"""
        query = """
        subscription autowatering_data($deviceId: GlobalID!) {
            autowateringData(deviceId: $deviceId) {
                __typename
                id
                time
              }
            }
        """
        variables = {"deviceId": relay.to_base64(types.Device, 0)}
        ws = get_ws_client(self.user)
        res = await ws.connect()
        assert res == (True, GRAPHQL_WS_PROTOCOL)
        await ws.send_json_to({"type": GQL_CONNECTION_INIT})
        await ws.send_json_to(
            {
                "type": GQL_START,
                "id": "demo_consumer",
                "payload": {"query": f"{query}", "variables": variables},
            }
        )
        response = await ws.receive_json_from()
        assert response["type"] == GQL_CONNECTION_ACK

        response = await ws.receive_json_from()
        assert response["type"] == GQL_DATA
        assert response["id"] == "demo_consumer"
        assert response["payload"]["errors"][0]["message"] == "['设备不存在']"
