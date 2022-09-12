from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.testcases import TestCase

from home.utils import GraphQLTestCase

from .models import Avatar, Config


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
