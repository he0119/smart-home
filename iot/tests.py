from django.contrib.auth import get_user_model
from graphql_jwt.testcases import JSONWebTokenTestCase

from .models import AutowateringData, Device


class DeviceTests(JSONWebTokenTestCase):
    fixtures = ['user', 'iot']

    def setUp(self):
        self.user = get_user_model().objects.get(username='test')
        self.client.authenticate(self.user)

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
        self.assertEqual(set(names), set(['test']))
