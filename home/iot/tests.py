import json
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from graphql_jwt.testcases import JSONWebTokenTestCase

from .models import AutowateringData, Device


class DeviceTests(JSONWebTokenTestCase):
    fixtures = ['users', 'iot']

    def setUp(self):
        self.user = get_user_model().objects.get(username='test')
        self.client.authenticate(self.user)

    def test_get_device(self):
        """ 获取指定设备信息 """
        query = '''
            query device($id: ID!) {
                device(id: $id) {
                    id
                    name
                    deviceType
                    location
                }
            }
        '''
        test_device = Device.objects.get(name='test')
        variables = {'id': test_device.id}

        content = self.client.execute(query, variables)
        self.assertIsNone(content.errors)

        device = content.data['device']
        self.assertEqual(device['name'], test_device.name)
        self.assertEqual(device['deviceType'], test_device.device_type)
        self.assertEqual(device['location'], test_device.location)

    def test_get_devices(self):
        """ 获取所有设备信息 """
        query = '''
            query devices {
                devices {
                    id
                    name
                }
            }
        '''
        content = self.client.execute(query)
        self.assertIsNone(content.errors)

        names = [item['name'] for item in content.data['devices']]
        self.assertEqual(set(names), {'test', 'test2'})

    def test_get_devices_by_number(self):
        """ 获取指定数量的设备信息 """
        query = '''
            query devices($number: Int) {
                devices(number: $number) {
                    id
                    name
                }
            }
        '''
        variables = {'number': 1}

        content = self.client.execute(query, variables)
        self.assertIsNone(content.errors)

        names = [item['name'] for item in content.data['devices']]
        self.assertEqual(set(names), {'test'})

    def test_add_device(self):
        """ 测试添加设备 """
        mutation = '''
            mutation addDevice($input: AddDeviceInput!) {
                addDevice(input: $input) {
                    device {
                        __typename
                        id
                        name
                        deviceType
                        location
                    }
                }
            }
        '''
        variables = {
            'input': {
                'name': 'test2',
                'deviceType': 'sometype',
                'location': 'somelocation',
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)

        device = content.data['addDevice']['device']
        self.assertEqual(device['__typename'], 'DeviceType')
        self.assertEqual(device['name'], 'test2')
        self.assertEqual(device['deviceType'], 'sometype')
        self.assertEqual(device['location'], 'somelocation')

    def test_delete_device(self):
        """ 测试删除设备 """
        mutation = '''
            mutation deleteDevice($input: DeleteDeviceInput!) {
                deleteDevice(input: $input) {
                    deletedId
                }
            }
        '''

        test_device = Device.objects.get(name='test')
        variables = {'input': {'deviceId': test_device.id}}

        # 确认自动浇水有数据
        self.assertNotEqual(list(AutowateringData.objects.all()), [])

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)

        deletedId = content.data['deleteDevice']['deletedId']
        self.assertEqual(deletedId, str(test_device.id))
        with self.assertRaises(Device.DoesNotExist):
            Device.objects.get(name='test')
        # 确认是否同时删除自动浇水数据
        self.assertEqual(list(AutowateringData.objects.all()), [])

    def test_update_device(self):
        """ 测试更新设备 """
        mutation = '''
            mutation updateDevice($input: UpdateDeviceInput!) {
                updateDevice(input: $input) {
                    device {
                        __typename
                        id
                        name
                        deviceType
                        location
                    }
                }
            }
        '''
        variables = {
            'input': {
                'id': 1,
                'name': 'newtest',
                'deviceType': 'newdevicetype',
                'location': 'newlocation',
            }
        }

        old_Device = Device.objects.get(pk=1)
        self.assertEqual(old_Device.name, 'test')

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)
        device = content.data['updateDevice']['device']

        self.assertEqual(device['__typename'], 'DeviceType')
        self.assertEqual(device['id'], '1')
        self.assertEqual(device['name'], 'newtest')
        self.assertEqual(device['deviceType'], 'newdevicetype')
        self.assertEqual(device['location'], 'newlocation')

    def test_set_device(self):
        """ 测试设置设备状态 """
        mutation = '''
            mutation setDevice($input: SetDeviceInput!) {
                setDevice(input: $input) {
                    device {
                        __typename
                        id
                    }
                }
            }
        '''
        variables = {
            'input': {
                'id': 1,
                'key': 'valve1',
                'value': '1',
                'valueType': 'bool',
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)
        device = content.data['setDevice']['device']

        self.assertEqual(device['__typename'], 'DeviceType')
        self.assertEqual(device['id'], '1')

    def test_get_device_data(self):
        """ 获取指定设备数据 """
        query = '''
            query deviceData($deviceId: ID!, $number: Int) {
                deviceData(deviceId: $deviceId, number: $number) {
                    temperature
                    humidity
                }
            }
        '''
        variables = {'deviceId': 1}

        content = self.client.execute(query, variables)
        self.assertIsNone(content.errors)

        data = [item['temperature'] for item in content.data['deviceData']]
        self.assertEqual(set(data), {1.0, 2.0, 3.0})

    def test_get_device_data_by_number(self):
        """ 获取指定数量的设备数据 """
        query = '''
            query deviceData($deviceId: ID!, $number: Int) {
                deviceData(deviceId: $deviceId, number: $number) {
                    temperature
                    humidity
                }
            }
        '''
        variables = {'deviceId': 1, 'number': 1}

        content = self.client.execute(query, variables)
        self.assertIsNone(content.errors)

        data = [item['temperature'] for item in content.data['deviceData']]
        self.assertEqual(set(data), {3.0})


class WebHookTests(TestCase):
    fixtures = ['users', 'iot']

    def test_webhook_get(self):
        """ 测试上报地址是否正常运行 """
        response = self.client.get(reverse('iot:iot'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'iot': 'working'})

    def test_client_connected(self):
        """ 测试客户端连接 """
        webhook_data = {
            'username': 'admin',
            'proto_ver': 4,
            'keepalive': 15,
            'ipaddress': '221.10.55.132',
            'connected_at': 1607658682703,
            'clientid': '1',
            'action': 'client_connected'
        }
        response = self.client.post(reverse('iot:iot'),
                                    data=json.dumps(webhook_data),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)

        device = Device.objects.get(pk=1)
        self.assertEqual(device.is_online, True)

    def test_client_connected_not_iot(self):
        """ 测试客户端连接，但不是物联网设备 """
        webhook_data = {
            'username': 'admin',
            'proto_ver': 4,
            'keepalive': 15,
            'ipaddress': '221.10.55.132',
            'connected_at': 1607658682703,
            'clientid': 'notiot',
            'action': 'client_connected'
        }
        response = self.client.post(reverse('iot:iot'),
                                    data=json.dumps(webhook_data),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)

        device = Device.objects.get(pk=1)
        self.assertEqual(device.is_online, False)
        device = Device.objects.get(pk=2)
        self.assertEqual(device.is_online, True)

    def test_client_connected_not_exist(self):
        """ 测试客户端连接，但不是设备不存在 """
        webhook_data = {
            'username': 'admin',
            'proto_ver': 4,
            'keepalive': 15,
            'ipaddress': '221.10.55.132',
            'connected_at': 1607658682703,
            'clientid': '3',
            'action': 'client_connected'
        }
        response = self.client.post(reverse('iot:iot'),
                                    data=json.dumps(webhook_data),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'iot': 'working'})

    def test_client_disconnected(self):
        """ 测试客户端断开连接 """
        webhook_data = {
            'username': 'admin',
            'reason': 'keepalive_timeout',
            'clientid': '2',
            'action': 'client_disconnected'
        }
        response = self.client.post(reverse('iot:iot'),
                                    data=json.dumps(webhook_data),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)

        device = Device.objects.get(pk=2)
        self.assertEqual(device.is_online, False)

    def test_client_disconnected_not_iot(self):
        """ 测试客户端断开连接，但不是物联网设备 """
        webhook_data = {
            'username': 'admin',
            'reason': 'keepalive_timeout',
            'clientid': 'notiot',
            'action': 'client_disconnected'
        }
        response = self.client.post(reverse('iot:iot'),
                                    data=json.dumps(webhook_data),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)

        device = Device.objects.get(pk=1)
        self.assertEqual(device.is_online, False)
        device = Device.objects.get(pk=2)
        self.assertEqual(device.is_online, True)

    def test_client_disconnected_not_exist(self):
        """ 测试客户端断开连接，但不是设备不存在 """
        webhook_data = {
            'username': 'admin',
            'reason': 'keepalive_timeout',
            'clientid': '3',
            'action': 'client_disconnected'
        }
        response = self.client.post(reverse('iot:iot'),
                                    data=json.dumps(webhook_data),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'iot': 'working'})

    def test_message_publish(self):
        """ 测试上报数据 """
        webhook_data = {
            'ts': 1607658685693,
            'topic': 'device/1/status',
            'retain': False,
            'qos': 0,
            'payload':
            '{"device_id":1,"timestamp":1607658685,"data":{"temperature":4.0,"humidity":0,"valve1":false,"valve2":false,"valve3":false,"pump":false,"valve1_delay":60,"valve2_delay":60,"valve3_delay":60,"pump_delay":60,"wifi_signal":-43}}',
            'from_username': 'admin',
            'from_client_id': '1',
            'action': 'message_publish'
        }
        response = self.client.post(reverse('iot:iot'),
                                    data=json.dumps(webhook_data),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)

        autowatering_data = AutowateringData.objects.last()
        self.assertEqual(autowatering_data.temperature, 4.0)
        self.assertEqual(autowatering_data.wifi_signal, -43)

    def test_message_publish_not_iot(self):
        """ 测试上报数据，但不是物联网设备 """
        webhook_data = {
            'ts': 1607658685693,
            'topic': 'device/1/status',
            'retain': False,
            'qos': 0,
            'payload':
            '{"device_id":1,"timestamp":1607658685,"data":{"temperature":4.0,"humidity":0,"valve1":false,"valve2":false,"valve3":false,"pump":false,"valve1_delay":60,"valve2_delay":60,"valve3_delay":60,"pump_delay":60,"wifi_signal":-43}}',
            'from_username': 'admin',
            'from_client_id': 'notiot',
            'action': 'message_publish'
        }
        response = self.client.post(reverse('iot:iot'),
                                    data=json.dumps(webhook_data),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)

        autowatering_data = AutowateringData.objects.last()
        self.assertEqual(autowatering_data.id, 3)

    def test_message_publish_not_exist(self):
        """ 测试上报数据，但不是设备不存在 """
        webhook_data = {
            'ts': 1607658685693,
            'topic': 'device/1/status',
            'retain': False,
            'qos': 0,
            'payload':
            '{"device_id":1,"timestamp":1607658685,"data":{"temperature":4.0,"humidity":0,"valve1":false,"valve2":false,"valve3":false,"pump":false,"valve1_delay":60,"valve2_delay":60,"valve3_delay":60,"pump_delay":60,"wifi_signal":-43}}',
            'from_username': 'admin',
            'from_client_id': '3',
            'action': 'message_publish'
        }
        response = self.client.post(reverse('iot:iot'),
                                    data=json.dumps(webhook_data),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)

        autowatering_data = AutowateringData.objects.last()
        self.assertEqual(autowatering_data.id, 3)
        self.assertEqual(response.json(), {'iot': 'working'})
