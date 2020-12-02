from django.contrib.auth import get_user_model
from graphql_jwt.testcases import JSONWebTokenTestCase

from .models import MiPush


class DeviceTests(JSONWebTokenTestCase):
    fixtures = ['users', 'push']

    def setUp(self):
        self.user = get_user_model().objects.get(username='test')
        self.client.authenticate(self.user)

    def test_get_mipush(self):
        """ 获取当前用户的注册标识码 """
        query = '''
            query miPush {
                miPush {
                    user {
                        username
                    }
                    enable
                    regId
                }
            }
        '''
        content = self.client.execute(query)
        self.assertIsNone(content.errors)
        self.assertEqual(content.data['miPush']['user']['username'], 'test')
        self.assertEqual(content.data['miPush']['enable'], True)
        self.assertEqual(content.data['miPush']['regId'], 'regidofuser1')
