from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.testcases import TestCase
from strawberry_django_plus import relay

from home.utils import GraphQLTestCase

from . import types
from .models import Avatar, Config, Session
from .tasks import clear_sessions


class ModelTests(TestCase):
    fixtures = ["users"]

    def test_avatar_str(self):
        avatar = Avatar.objects.get(pk=1)

        self.assertEqual(str(avatar), "test")

    def test_config_str(self):
        config = Config.objects.get(pk=1)

        self.assertEqual(str(config), "key")


class UserTests(GraphQLTestCase):
    fixtures = ["users"]

    def setUp(self):
        self.user = get_user_model().objects.get(username="test")
        self.user_without_configs = get_user_model().objects.get(username="test2")

    def test_login(self):
        """测试登录"""
        query = """
            mutation login($input: LoginInput!) {
                login(input: $input) {
                    ... on User {
                        username
                    }
                }
            }
        """
        variables = {
            "input": {
                "username": "test",
                "password": "12345678",
            }
        }

        content = self.client.execute(query, variables)

        user = content.data["login"]
        self.assertEqual(user["username"], "test")

        query = """
            query viewer {
                viewer {
                    username
                    avatarUrl
                }
            }
        """
        content = self.client.execute(query)
        self.assertEqual(content.data["viewer"]["username"], "test")

    def test_login_wrong_password(self):
        """测试密码错误"""
        query = """
            mutation login($input: LoginInput!) {
                login(input: $input) {
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
                "username": "test",
                "password": "wrong",
            }
        }
        content = self.client.execute(query, variables)

        data = content.data["login"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "用户名或密码错误")

        query = """
            query viewer {
                viewer {
                    username
                    avatarUrl
                }
            }
        """
        content = self.client.execute(query, asserts_errors=False)
        self.assertIsNotNone(content.errors)

    def test_logout(self):
        """测试登出"""
        self.client.authenticate(self.user)

        query = """
            mutation logout {
                logout {
                    ... on User {
                        username
                    }
                }
            }
        """
        content = self.client.execute(query)
        user = content.data["logout"]
        self.assertEqual(user["username"], "test")

        query = """
            query viewer {
                viewer {
                    username
                }
            }
        """
        content = self.client.execute(query, asserts_errors=False)
        self.assertIsNotNone(content.errors)

    def test_get_user(self):
        self.client.authenticate(self.user)
        query = """
            query viewer {
                viewer {
                    username
                    avatarUrl
                }
            }
        """
        content = self.client.execute(query)
        self.assertIsNone(content.errors)
        self.assertEqual(content.data["viewer"]["username"], "test")
        self.assertEqual(content.data["viewer"]["avatarUrl"], "/avatar_pictures/1.jpg")

    def test_unauthenticate_user(self):
        query = """
            query viewer {
                viewer {
                    username
                }
            }
        """
        content = self.client.execute(query, asserts_errors=False)
        self.assertIsNotNone(content.errors)

    def test_get_configs(self):
        self.client.authenticate(self.user)
        query = """
            query viewer {
                viewer {
                    configs {
                        key
                        value
                    }
                }
            }
        """
        content = self.client.execute(query)
        self.assertIsNone(content.errors)

        configs = content.data["viewer"]["configs"]
        self.assertEqual(configs[0], {"key": "key", "value": "value"})

    def test_get_configs_not_exist(self):
        self.client.authenticate(self.user_without_configs)
        query = """
            query viewer {
                viewer {
                    configs {
                        key
                        value
                    }
                }
            }
        """
        content = self.client.execute(query)
        self.assertIsNone(content.errors)

        configs = content.data["viewer"]["configs"]
        self.assertListEqual(configs, [])

    def test_update_config(self):
        self.client.authenticate(self.user)
        query = """
            mutation updateConfig($input: UpdateConfigInput!) {
                updateConfig(input: $input) {
                    ... on Config {
                        key
                        value
                    }
                }
            }
        """
        variables = {
            "input": {
                "key": "key",
                "value": "new_value",
            }
        }

        content = self.client.execute(query, variables)
        self.assertIsNone(content.errors)

        config = content.data["updateConfig"]
        self.assertEqual(config["key"], "key")
        self.assertEqual(config["value"], "new_value")

    def test_update_config_not_exist(self):
        self.client.authenticate(self.user)
        self.assertEqual(Config.objects.count(), 1)

        query = """
            mutation updateConfig($input: UpdateConfigInput!) {
                updateConfig(input: $input) {
                    ... on Config {
                        key
                        value
                    }
                }
            }
        """
        variables = {
            "input": {
                "key": "new_key",
                "value": "new_value",
            }
        }

        content = self.client.execute(query, variables)
        self.assertIsNone(content.errors)

        config = content.data["updateConfig"]
        self.assertEqual(config["key"], "new_key")
        self.assertEqual(config["value"], "new_value")
        self.assertEqual(Config.objects.count(), 2)

    def test_delete_config(self):
        self.client.authenticate(self.user)
        self.assertEqual(Config.objects.count(), 1)

        query = """
            mutation deleteConfig($input: DeleteConfigInput!) {
                deleteConfig(input: $input) {
                    ... on Config {
                        key
                        value
                    }
                    ... on OperationInfo {
                        messages {
                            field
                            kind
                            message
                        }
                    }
                }
            }
        """
        variables = {
            "input": {
                "key": "key",
            }
        }

        content = self.client.execute(query, variables)
        self.assertIsNone(content.errors)

        self.assertEqual(Config.objects.count(), 0)

    def test_delete_config_not_exist(self):
        self.client.authenticate(self.user)
        self.assertEqual(Config.objects.count(), 1)

        query = """
            mutation deleteConfig($input: DeleteConfigInput!) {
                deleteConfig(input: $input) {
                    ... on Config {
                        key
                        value
                    }
                    ... on OperationInfo {
                        messages {
                            field
                            kind
                            message
                        }
                    }
                }
            }
        """
        variables = {
            "input": {
                "key": "not_exist",
            }
        }

        content = self.client.execute(query, variables)
        self.assertIsNone(content.errors)

        self.assertEqual(Config.objects.count(), 1)


class UserAvatarTests(GraphQLTestCase):
    fixtures = ["users"]

    def setUp(self):
        self.user = get_user_model().objects.get(username="test")
        self.user_without_avatar = get_user_model().objects.get(username="test2")

    def test_avatar_not_exist(self):
        """测试头像不存在的情况"""
        self.client.authenticate(self.user_without_avatar)
        query = """
            query viewer {
                viewer {
                    username
                    avatarUrl
                }
            }
        """
        content = self.client.execute(query)
        self.assertIsNone(content.errors)
        self.assertEqual(content.data["viewer"]["username"], "test2")
        self.assertEqual(content.data["viewer"]["avatarUrl"], None)

    def test_update_avatar(self):
        self.client.authenticate(self.user_without_avatar)

        test_file = SimpleUploadedFile(
            name="test.txt", content="file_text".encode("utf-8")
        )

        mutation = """
            mutation updateAvatar($input: UpdateAvatarInput!) {
                updateAvatar(input: $input) {
                    ... on Avatar {
                        avatar {
                            name
                            url
                        }
                    }
                }
            }
        """
        variables = {
            "input": {
                "file": None,
            }
        }

        content = self.client.execute(mutation, variables, files={"input": test_file})
        self.assertIsNone(content.errors)

        avatar = content.data["updateAvatar"]["avatar"]["url"]
        self.assertTrue(avatar.startswith("/avatar_pictures/2"))

    def test_update_avatar_already_exist(self):
        self.client.authenticate(self.user)

        test_file = SimpleUploadedFile(
            name="test.txt", content="file_text".encode("utf-8")
        )

        mutation = """
            mutation updateAvatar($input: UpdateAvatarInput!) {
                updateAvatar(input: $input) {
                    ... on Avatar {
                        avatar {
                            url
                        }
                    }
                }
            }
        """
        variables = {
            "input": {
                "file": None,
            }
        }

        content = self.client.execute(mutation, variables, files={"input": test_file})
        self.assertIsNone(content.errors)

        avatar = content.data["updateAvatar"]["avatar"]["url"]
        self.assertTrue(avatar.startswith("/avatar_pictures/1"))


class SessionTests(GraphQLTestCase):
    fixtures = ["users"]

    def setUp(self):
        self.user = get_user_model().objects.get(username="test")
        self.client.authenticate(self.user)

    def test_get_session(self):
        """测试获取用户的会话"""
        query = """
            query viewer {
                viewer {
                    session {
                        id
                        isValid
                        isCurrent
                        ip
                    }
                }
            }
        """
        content = self.client.execute(
            query, headers={"HTTP_X_FORWARDED_FOR": "1.1.1.1"}
        )

        data = content.data["viewer"]["session"]
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["isValid"], False)
        self.assertEqual(data[0]["isCurrent"], False)
        self.assertEqual(data[0]["ip"], "127.0.0.1")
        self.assertEqual(data[1]["isValid"], True)
        self.assertEqual(data[1]["isCurrent"], True)
        self.assertEqual(data[1]["ip"], None)

        session = Session.objects.get(pk="b3hywvvlnly7unshlqu6yhrsyps3phjq")
        session_data = session.get_decoded()
        self.assertEqual("1", session_data.get("_auth_user_id"))

        # 再次请求，这次应该能够获取到正确的 IP 地址
        # 因为在上一次请求中，已经将 IP 地址写入到了 session 中
        content = self.client.execute(
            query, headers={"HTTP_X_FORWARDED_FOR": "1.1.1.1"}
        )

        data = content.data["viewer"]["session"]
        self.assertEqual(len(data), 2)
        self.assertEqual(data[1]["isValid"], True)
        self.assertEqual(data[1]["isCurrent"], True)
        self.assertEqual(data[1]["ip"], "1.1.1.1")

    def test_delete_session(self):
        mutation = """
            mutation deleteSession($input: DeleteSessionInput!) {
                deleteSession(input: $input) {
                    ... on Session {
                        id
                    }
                }
            }
        """
        variables = {
            "input": {
                "id": relay.to_base64(
                    types.Session, "b3hywvvlnly7unshlqu6yhrsyps3phjq"
                ),
            }
        }

        content = self.client.execute(mutation, variables)

        with self.assertRaises(Session.DoesNotExist):
            Session.objects.get(pk="b3hywvvlnly7unshlqu6yhrsyps3phjq")

    def test_delete_session_not_exist(self):
        """测试删除不存在的会话"""
        mutation = """
            mutation deleteSession($input: DeleteSessionInput!) {
                deleteSession(input: $input) {
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
                "id": relay.to_base64(types.Session, "123"),
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["deleteSession"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "会话不存在")

    def test_delete_session_other_user(self):
        """测试删除其他用户的会话"""
        mutation = """
            mutation deleteSession($input: DeleteSessionInput!) {
                deleteSession(input: $input) {
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
                "id": relay.to_base64(
                    types.Session, "voj866ttugmcns05agvl2bxetqel47ln"
                ),
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["deleteSession"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "只能删除自己的会话")


class TaskTests(TestCase):
    fixtures = ["users"]

    def test_clear_sessions(self):
        """测试清理过期的会话"""
        self.assertEqual(Session.objects.count(), 2)
        clear_sessions()
        self.assertEqual(Session.objects.count(), 0)
