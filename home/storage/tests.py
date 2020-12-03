from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from graphql_jwt.testcases import JSONWebTokenTestCase

from .models import Item, Storage


def query_set_to_list(query_set):
    """ 转换 TreeQuerySet 到列表 """
    return [i for i in query_set]


class StorageModelTests(TestCase):
    fixtures = ['users', 'storage']

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


class StorageTests(JSONWebTokenTestCase):
    fixtures = ['users', 'storage']

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

    def test_add_storage(self):
        mutation = '''
            mutation addStorage($input: AddStorageInput!) {
                addStorage(input: $input) {
                    storage {
                        __typename
                        id
                        name
                        description
                    }
                }
            }
        '''
        variables = {
            'input': {
                'name': 'test',
                'description': 'some',
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)

        storage = content.data['addStorage']['storage']
        self.assertEqual(storage['__typename'], 'StorageType')
        self.assertEqual(storage['name'], 'test')
        self.assertEqual(storage['description'], 'some')

    def test_delete_storage(self):
        mutation = '''
            mutation deleteStorage($id: ID!) {
                deleteStorage(id: $id) {
                    deletedId
                }
            }
        '''

        toolbox = Storage.objects.get(name='工具箱')
        variables = {'id': toolbox.id}

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)

        deletedId = content.data['deleteStorage']['deletedId']
        self.assertEqual(deletedId, str(toolbox.id))
        with self.assertRaises(Storage.DoesNotExist):
            Storage.objects.get(name='工具箱')

    def test_update_storage(self):
        mutation = '''
            mutation updateStorage($input: UpdateStorageInput!) {
                updateStorage(input: $input) {
                    storage {
                        __typename
                        id
                        name
                        description
                        parent {
                            __typename
                            id
                        }
                    }
                }
            }
        '''
        variables = {
            'input': {
                'id': 1,
                'name': 'test',
                'description': 'some',
            }
        }

        old_storage = Storage.objects.get(pk=1)
        self.assertEqual(old_storage.name, '阳台')

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)
        storage = content.data['updateStorage']['storage']

        self.assertEqual(storage['__typename'], 'StorageType')
        self.assertEqual(storage['id'], '1')
        self.assertEqual(storage['name'], 'test')
        self.assertEqual(storage['description'], 'some')


class ItemTests(JSONWebTokenTestCase):
    fixtures = ['users', 'storage']

    def setUp(self):
        self.user = get_user_model().objects.get(username='test')
        self.client.authenticate(self.user)

    def test_get_items(self):
        query = '''
            query items {
                items {
                    name
                }
            }
        '''
        content = self.client.execute(query)
        self.assertIsNone(content.errors)
        names = [item['name'] for item in content.data['items']]
        self.assertEqual(set(names), set(['雨伞', '口罩']))

    def test_get_item(self):
        umbrella = Item.objects.get(name='雨伞')

        query = f'''
            query item {{
                item(id: {umbrella.id}) {{
                    name
                }}
            }}
        '''
        content = self.client.execute(query)
        self.assertIsNone(content.errors)

        name = content.data['item']['name']
        self.assertEqual(name, umbrella.name)

    def test_add_item(self):
        mutation = '''
            mutation addItem($input: AddItemInput!) {
                addItem(input: $input) {
                    item {
                        __typename
                        id
                        name
                        number
                        storage {
                            id
                            name
                        }
                        description
                        price
                        expirationDate
                        updateDate
                        editor {
                            username
                        }
                    }
                }
            }
        '''
        variables = {
            'input': {
                'name': 'test',
                'number': 1,
                'storage': {
                    'id': 1
                },
                'description': 'some',
                'price': '12.0',
                'expirationDate': None,
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)

        item = content.data['addItem']['item']
        self.assertEqual(item['__typename'], 'ItemType')
        self.assertEqual(item['name'], 'test')
        self.assertEqual(item['description'], 'some')

    def test_delete_item(self):
        mutation = '''
            mutation deleteItem($id: ID!) {
                deleteItem(id: $id) {
                    deletedId
                }
            }
        '''

        umbrella = Item.objects.get(name='雨伞')
        variables = {'id': umbrella.id}

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)

        deletedId = content.data['deleteItem']['deletedId']
        self.assertEqual(deletedId, str(umbrella.id))
        with self.assertRaises(Item.DoesNotExist):
            Item.objects.get(name='雨伞')

    def test_update_item(self):
        mutation = '''
            mutation updateItem($input: UpdateItemInput!) {
                updateItem(input: $input) {
                    item {
                        __typename
                        id
                        name
                        number
                        storage {
                            id
                            name
                        }
                        description
                        price
                        expirationDate
                        updateDate
                        editor {
                            username
                        }
                    }
                }
            }
        '''
        expiration_date = timezone.now()
        variables = {
            'input': {
                'id': 1,
                'name': 'test',
                'number': 2,
                'storage': {
                    'id': 2
                },
                'description': 'some',
                'price': '12.0',
                'expirationDate': expiration_date.isoformat(),
            }
        }

        old_item = Item.objects.get(pk=1)
        self.assertEqual(old_item.name, '雨伞')

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)
        item = content.data['updateItem']['item']

        self.assertEqual(item['__typename'], 'ItemType')
        self.assertEqual(item['id'], '1')
        self.assertEqual(item['name'], 'test')
        self.assertEqual(item['number'], 2)
        self.assertEqual(item['description'], 'some')
        self.assertEqual(item['storage']['id'], '2')
        self.assertEqual(item['price'], 12.0)
        self.assertEqual(item['expirationDate'], expiration_date.isoformat())