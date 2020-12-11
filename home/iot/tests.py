from django.contrib.auth import get_user_model
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
