from django.contrib.auth import get_user_model
from django.test import TestCase
from graphql_jwt.testcases import JSONWebTokenTestCase

from .models import Storage


def query_set_to_list(query_set):
    """ 转换 TreeQuerySet 到列表 """
    return [i for i in query_set]


class StorageModelTests(TestCase):
    fixtures = ['tests.json']

    def test_ancestors(self):
        """ 测试父节点 """
        balcony = Storage.objects.get(name="阳台")
        locker = Storage.objects.get(name="阳台储物柜")
        toolbox = Storage.objects.get(name="工具箱")
        toolbox2 = Storage.objects.get(name="工具箱2")

        self.assertEqual(balcony.parent, None)
        self.assertEqual(query_set_to_list(balcony.get_ancestors()), [])

        self.assertEqual(locker.parent, balcony)
        self.assertEqual(query_set_to_list(locker.get_ancestors()), [balcony])

        self.assertEqual(toolbox.parent, locker)
        self.assertEqual(query_set_to_list(toolbox.get_ancestors()),
                         [balcony, locker])

    def test_children(self):
        balcony = Storage.objects.get(name="阳台")
        locker = Storage.objects.get(name="阳台储物柜")
        toolbox = Storage.objects.get(name="工具箱")
        toolbox2 = Storage.objects.get(name="工具箱2")

        self.assertEqual(query_set_to_list(balcony.get_children()), [locker])

        self.assertEqual(query_set_to_list(locker.get_children()),
                         [toolbox, toolbox2])

        self.assertEqual(query_set_to_list(toolbox.get_children()), [])


class UserTests(JSONWebTokenTestCase):
    fixtures = ['tests.json']

    def setUp(self):
        self.user = get_user_model().objects.get(username='test')

    def test_get_user(self):
        self.client.authenticate(self.user)
        query = '''
            query me {
                me {
                    username
                }
            }
        '''
        content = self.client.execute(query)
        self.assertIsNone(content.errors)
        self.assertEqual(content.data['me'], {'username': 'test'})

    def test_unauthenticate_user(self):
        query = '''
            query me {
                me {
                    username
                }
            }
        '''
        content = self.client.execute(query)
        self.assertIsNotNone(content.errors)

class StoragesTests(JSONWebTokenTestCase):
    fixtures = ['tests.json']

    def setUp(self):
        self.user = get_user_model().objects.get(username='test')
        self.client.authenticate(self.user)

    def test_get_storages(self):
        query = '''
            query storage {
                storages {
                    name
                }
            }
        '''
        content = self.client.execute(query)
        self.assertIsNone(content.errors)
        names = [storage['name'] for storage in content.data['storages']]
        self.assertEqual(set(names), set(['阳台', '阳台储物柜', '工具箱', '工具箱2']))

    def test_get_storage(self):
        toolbox = Storage.objects.get(name='工具箱')

        query = f'''
            query storage {{
                storage(id: {toolbox.id}) {{
                    name
                }}
            }}
        '''
        content = self.client.execute(query)
        self.assertIsNone(content.errors)
        name = content.data['storage']['name']
        self.assertEqual(name, toolbox.name)
