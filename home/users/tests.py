from home.users.tasks import clear_expired_tokens
from django.contrib.auth import get_user_model
from django.test.testcases import TestCase
from graphql_jwt.testcases import JSONWebTokenTestCase


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
                }
            }
        """
        content = self.client.execute(query)
        self.assertIsNone(content.errors)
        self.assertEqual(content.data["viewer"], {"username": "test"})

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


class TokenTests(TestCase):
    fixtures = ["users"]

    def test_clear_expired_tokens(self):
        clear_expired_tokens()
