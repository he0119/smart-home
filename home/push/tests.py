from django.contrib.auth import get_user_model
from django.test import TestCase
from graphql_jwt.testcases import JSONWebTokenTestCase

from home.push.tasks import (PushChannel, build_message, get_enable_reg_ids,
                             get_enable_reg_ids_except_user)


class PushTests(JSONWebTokenTestCase):
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

        mipush = content.data['miPush']
        self.assertEqual(mipush['user']['username'], 'test')
        self.assertEqual(mipush['enable'], True)
        self.assertEqual(mipush['regId'], 'regidofuser1')

    def test_get_mipush_key(self):
        """ 获取当前软件的 AppID 与 AppKey """
        query = '''
            query miPushKey {
                miPushKey {
                    appId
                    appKey
                }
            }
        '''
        content = self.client.execute(query)
        self.assertIsNone(content.errors)

        mipush_key = content.data['miPushKey']
        self.assertEqual(mipush_key['appId'], 'app_id')
        self.assertEqual(mipush_key['appKey'], 'app_key')

    def test_update_mipush(self):
        mutation = '''
            mutation updateMiPush($input: UpdateMiPushInput!) {
                updateMiPush(input: $input) {
                    miPush {
                        user {
                            username
                        }
                        regId
                    }
                }
            }
        '''
        variables = {
            'input': {
                'regId': 'testRegId',
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)

        mipush = content.data['updateMiPush']['miPush']
        self.assertEqual(mipush['user']['username'], 'test')
        self.assertEqual(mipush['regId'], 'testRegId')

    def test_get_enable_reg_ids(self):
        """ 测试获取所有启用用户的注册标识码 """
        reg_ids = get_enable_reg_ids()
        self.assertEqual(reg_ids, ['regidofuser1'])

    def test_get_enable_reg_ids_except_user(self):
        """ 测试获取除指定用户以外的所有启用用户的注册标识码 """
        reg_ids = get_enable_reg_ids_except_user(self.user)
        self.assertEqual(reg_ids, [])


class EmptyPushTests(JSONWebTokenTestCase):
    """ 测试数据库是空的情况 """
    fixtures = ['users']

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
        self.assertEqual(str(content.errors[0]), '推送未绑定')

    def test_update_mipush_without_create(self):
        """ 在没有创建的情况更新，应该会自动创建 """
        mutation = '''
            mutation updateMiPush($input: UpdateMiPushInput!) {
                updateMiPush(input: $input) {
                    miPush {
                        user {
                            username
                        }
                        regId
                    }
                }
            }
        '''
        variables = {
            'input': {
                'regId': 'testRegId',
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)

        mipush = content.data['updateMiPush']['miPush']
        self.assertEqual(mipush['user']['username'], 'test')
        self.assertEqual(mipush['regId'], 'testRegId')

    def test_get_enable_reg_ids(self):
        """ 测试获取所有启用用户的注册标识码 """
        reg_ids = get_enable_reg_ids()
        self.assertEqual(reg_ids, [])

    def test_get_enable_reg_ids_except_user(self):
        """ 测试获取除指定用户以外的所有启用用户的注册标识码 """
        reg_ids = get_enable_reg_ids_except_user(self.user)
        self.assertEqual(reg_ids, [])


class DisabledPushTests(TestCase):
    """ 测试一些用户推送禁用的情况 """
    fixtures = ['users', 'push_disabled']

    def setUp(self):
        self.user = get_user_model().objects.get(username='test')

    def test_get_enable_reg_ids(self):
        """ 测试获取所有启用用户的注册标识码 """
        reg_ids = get_enable_reg_ids()
        self.assertEqual(reg_ids, ['regidofuser2'])

    def test_get_enable_reg_ids_except_user(self):
        """ 测试获取除指定用户以外的所有启用用户的注册标识码 """
        reg_ids = get_enable_reg_ids_except_user(self.user)
        self.assertEqual(reg_ids, ['regidofuser2'])


class MiPushMessageTest(TestCase):
    fixtures = ['users', 'push']

    def test_mipush_message(self):
        message = build_message(title='test',
                                description='test description',
                                channel=None)

        message_dict = message.message_dict()
        self.assertEqual(message_dict['title'], 'test')
        self.assertEqual(message_dict['description'], 'test description')
        self.assertLessEqual(message_dict['notify_id'], 10000)
        self.assertEqual(message_dict['extra.notify_effect'], '1')
        self.assertEqual(message_dict['extra.notification_style_type'], '1')

    def test_board_channel_mipush_message(self):
        message = build_message(title='test',
                                description='test description',
                                channel=PushChannel.BOARD.value)

        message_dict = message.message_dict()
        self.assertEqual(message_dict['title'], 'test')
        self.assertEqual(message_dict['description'], 'test description')
        self.assertLessEqual(message_dict['notify_id'], 10000)
        self.assertEqual(message_dict['extra.notify_effect'], '1')
        self.assertEqual(message_dict['extra.notification_style_type'], '1')

        self.assertEqual(message_dict['extra.channel_id'], 'pre84')
        self.assertEqual(message_dict['extra.channel_name'], '留言板消息')
