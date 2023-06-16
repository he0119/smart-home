from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from strawberry import relay

from home.push.tasks import (
    build_message,
    get_enable_reg_ids,
    get_enable_reg_ids_except_user,
)
from home.tests import GraphQLTestCase

from . import types
from .models import MiPush
from .tasks import push_to_users, sender


class ModelTests(TestCase):
    fixtures = ["users", "push"]

    def test_mipush_str(self):
        mipush = MiPush.objects.get(pk=1)

        self.assertEqual(str(mipush), "test")


class PushTests(GraphQLTestCase):
    fixtures = ["users", "push"]

    def setUp(self):
        self.user = get_user_model().objects.get(username="test")
        self.client.authenticate(self.user)

    def test_get_mipush(self):
        """获取当前用户的注册标识码"""
        query = """
            query miPush($deviceId: String!) {
                miPush(deviceId: $deviceId) {
                    user {
                        username
                    }
                    enable
                    regId
                    deviceId
                    model
                }
            }
        """

        # 第一个设备
        variables = {"deviceId": "deviceidofuser1"}
        content = self.client.execute(query, variables)

        mipush = content.data["miPush"]
        self.assertEqual(mipush["user"]["username"], "test")
        self.assertEqual(mipush["enable"], True)
        self.assertEqual(mipush["regId"], "regidofuser1")
        self.assertEqual(mipush["model"], "modelofuser1")

        # 第二个设备
        variables = {"deviceId": "deviceid2ofuser1"}
        content = self.client.execute(query, variables)

        mipush = content.data["miPush"]
        self.assertEqual(mipush["user"]["username"], "test")
        self.assertEqual(mipush["enable"], True)
        self.assertEqual(mipush["regId"], "regid2ofuser1")
        self.assertEqual(mipush["model"], "model2ofuser1")

    def test_get_mipushs(self):
        """获取所有注册标识码"""
        query = """
            query miPushs {
                miPushs {
                    edges {
                        node {
                            user {
                                username
                            }
                            enable
                            regId
                            deviceId
                            model
                        }
                    }
                }
            }
        """
        content = self.client.execute(query)

        # 第一个设备
        mipush = content.data["miPushs"]["edges"][0]["node"]
        self.assertEqual(mipush["user"]["username"], "test")
        self.assertEqual(mipush["enable"], True)
        self.assertEqual(mipush["regId"], "regidofuser1")
        self.assertEqual(mipush["model"], "modelofuser1")

        # 第二个设备
        mipush = content.data["miPushs"]["edges"][1]["node"]
        self.assertEqual(mipush["user"]["username"], "test")
        self.assertEqual(mipush["enable"], True)
        self.assertEqual(mipush["regId"], "regid2ofuser1")
        self.assertEqual(mipush["model"], "model2ofuser1")

    def test_get_mipush_key(self):
        """获取当前软件的 AppID 与 AppKey"""
        query = """
            query miPushKey {
                miPushKey {
                    appId
                    appKey
                }
            }
        """
        content = self.client.execute(query)

        mipush_key = content.data["miPushKey"]
        self.assertEqual(mipush_key["appId"], "app_id")
        self.assertEqual(mipush_key["appKey"], "app_key")

    def test_get_mipush_via_node(self):
        query = """
            query miPush($id: GlobalID!) {
                mipush(id: $id) {
                    user {
                        username
                    }
                    enable
                    regId
                    deviceId
                    model
                }
            }
        """
        variables = {"id": relay.to_base64(types.MiPush, "1")}

        content = self.client.execute(query, variables)

        mipush = content.data["mipush"]
        self.assertEqual(mipush["user"]["username"], "test")
        self.assertEqual(mipush["enable"], True)
        self.assertEqual(mipush["regId"], "regidofuser1")
        self.assertEqual(mipush["model"], "modelofuser1")

    def test_update_mipush(self):
        mutation = """
            mutation updateMiPush($input: UpdateMiPushInput!) {
                updateMiPush(input: $input) {
                    ... on MiPush {
                        user {
                            username
                        }
                        regId
                        deviceId
                        model
                    }
                }
            }
        """
        variables = {
            "input": {
                "regId": "testRegId",
                "deviceId": "deviceidofuser1",
                "model": "modelofuser1",
            }
        }

        content = self.client.execute(mutation, variables)

        mipush = content.data["updateMiPush"]
        self.assertEqual(mipush["user"]["username"], "test")
        self.assertEqual(mipush["regId"], "testRegId")

    def test_get_enable_reg_ids(self):
        """测试获取所有启用用户的注册标识码"""
        reg_ids = get_enable_reg_ids()
        self.assertEqual(set(reg_ids), {"regidofuser1", "regid2ofuser1"})

    def test_get_enable_reg_ids_except_user(self):
        """测试获取除指定用户以外的所有启用用户的注册标识码"""
        reg_ids = get_enable_reg_ids_except_user(self.user)
        self.assertEqual(reg_ids, [])


class DifferentUserPushTests(GraphQLTestCase):
    fixtures = ["users", "push"]

    def setUp(self):
        self.user = get_user_model().objects.get(username="test2")
        self.client.authenticate(self.user)

    def test_update_mipush(self):
        """测试同一个设备更换用户名"""
        mutation = """
            mutation updateMiPush($input: UpdateMiPushInput!) {
                updateMiPush(input: $input) {
                    ... on MiPush {
                        user {
                            username
                        }
                        regId
                        deviceId
                        model
                    }
                }
            }
        """
        variables = {
            "input": {
                "regId": "testRegId",
                "deviceId": "deviceidofuser1",
                "model": "modelofuser1",
            }
        }

        content = self.client.execute(mutation, variables)

        mipush = content.data["updateMiPush"]
        self.assertEqual(mipush["user"]["username"], "test2")
        self.assertEqual(mipush["regId"], "testRegId")


class EmptyPushTests(GraphQLTestCase):
    """测试数据库是空的情况"""

    fixtures = ["users"]

    def setUp(self):
        self.user = get_user_model().objects.get(username="test")
        self.client.authenticate(self.user)

    def test_get_mipush(self):
        """获取当前用户的注册标识码"""
        query = """
            query miPush($deviceId: String!) {
                miPush(deviceId: $deviceId) {
                    id
                }
            }
        """
        variables = {"deviceId": "deviceidofuser1"}

        content = self.client.execute(query, variables)

        data = content.data["miPush"]
        self.assertEqual(data, None)

    def test_update_mipush_without_create(self):
        """在没有创建的情况更新，应该会自动创建"""
        mutation = """
            mutation updateMiPush($input: UpdateMiPushInput!) {
                updateMiPush(input: $input) {
                    ... on MiPush {
                        user {
                            username
                        }
                        regId
                        deviceId
                        model
                    }
                }
            }
        """
        variables = {
            "input": {
                "regId": "testRegId",
                "deviceId": "deviceidofuser1",
                "model": "modelofuser1",
            }
        }

        content = self.client.execute(mutation, variables)

        mipush = content.data["updateMiPush"]
        self.assertEqual(mipush["user"]["username"], "test")
        self.assertEqual(mipush["regId"], "testRegId")

    def test_get_enable_reg_ids(self):
        """测试获取所有启用用户的注册标识码"""
        reg_ids = get_enable_reg_ids()
        self.assertEqual(reg_ids, [])

    def test_get_enable_reg_ids_except_user(self):
        """测试获取除指定用户以外的所有启用用户的注册标识码"""
        reg_ids = get_enable_reg_ids_except_user(self.user)
        self.assertEqual(reg_ids, [])


class DisabledPushTests(TestCase):
    """测试一些用户推送禁用的情况"""

    fixtures = ["users", "push_disabled"]

    def setUp(self):
        self.user = get_user_model().objects.get(username="test")

    def test_get_enable_reg_ids(self):
        """测试获取所有启用用户的注册标识码"""
        reg_ids = get_enable_reg_ids()
        self.assertEqual(set(reg_ids), {"regidofuser2", "regid2ofuser2"})

    def test_get_enable_reg_ids_except_user(self):
        """测试获取除指定用户以外的所有启用用户的注册标识码"""
        reg_ids = get_enable_reg_ids_except_user(self.user)
        self.assertEqual(set(reg_ids), {"regidofuser2", "regid2ofuser2"})


class MiPushMessageTest(TestCase):
    fixtures = ["users", "push"]

    def test_mipush_message(self):
        message = build_message(
            title="test",
            description="test description",
            payload="/iot",
            is_important=False,
        )

        message_dict = message.message_dict()
        self.assertEqual(message_dict["title"], "test")
        self.assertEqual(message_dict["description"], "test description")
        self.assertLessEqual(message_dict["notify_id"], 10000)
        self.assertEqual(message_dict["payload"], "/iot")
        self.assertEqual(message_dict["extra.notification_style_type"], "1")

    def test_board_channel_mipush_message(self):
        message = build_message(
            title="test",
            description="test description",
            payload="/iot",
            is_important=True,
        )

        message_dict = message.message_dict()
        self.assertEqual(message_dict["title"], "test")
        self.assertEqual(message_dict["description"], "test description")
        self.assertLessEqual(message_dict["notify_id"], 10000)
        self.assertEqual(message_dict["payload"], "/iot")
        self.assertEqual(message_dict["extra.notification_style_type"], "1")

        self.assertEqual(message_dict["extra.channel_id"], "high_system")
        self.assertEqual(message_dict["extra.channel_name"], "服务提醒")


def mocked_sender_send(*args, **kwargs):
    """测试数据"""
    return None


class TaskTests(TestCase):
    fixtures = ["users", "push"]

    @mock.patch.object(sender, "send", side_effect=mocked_sender_send)
    def test_push_to_users(self, mock_send):
        push_to_users(["1"], "title", "description", "/iot")

        self.assertTrue(mock_send.call_args_list)

    @mock.patch.object(sender, "send", side_effect=mocked_sender_send)
    def test_push_to_users_without_secrets(self, mock_send):
        with self.settings(MI_PUSH_APP_SECRET=""):
            push_to_users(["1"], "title", "description", "/iot")

            self.assertFalse(mock_send.call_args_list)
