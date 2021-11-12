from django.contrib.auth import get_user_model
from django.test.testcases import TestCase
from graphql_jwt.testcases import JSONWebTokenTestCase

from home.users.tasks import clear_expired_tokens

from .models import Avatar


class ModelTests(TestCase):
    fixtures = ["users"]

    def test_avatar_str(self):
        avatar = Avatar.objects.get(pk=1)

        self.assertEqual(str(avatar), "test")


class UserTests(JSONWebTokenTestCase):
    fixtures = ["users"]

    def setUp(self):
        self.user = get_user_model().objects.get(username="test")

    def test_get_user(self):
        self.client.authenticate(self.user)
        query = """
            query viewer {
                viewer {
                    username
                    avatar
                }
            }
        """
        content = self.client.execute(query)
        self.assertIsNone(content.errors)
        self.assertEqual(content.data["viewer"]["username"], "test")
        self.assertEqual(content.data["viewer"]["avatar"], "/avatar_pictures/1.jpg")

    def test_unauthenticate_user(self):
        query = """
            query viewer {
                viewer {
                    username
                }
            }
        """
        content = self.client.execute(query)
        self.assertIsNotNone(content.errors)


class UserAvatarTests(JSONWebTokenTestCase):
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
                    avatar
                }
            }
        """
        content = self.client.execute(query)
        self.assertIsNone(content.errors)
        self.assertEqual(content.data["viewer"]["username"], "test2")
        self.assertEqual(content.data["viewer"]["avatar"], None)


class TokenTests(TestCase):
    fixtures = ["users"]

    def test_clear_expired_tokens(self):
        clear_expired_tokens()
