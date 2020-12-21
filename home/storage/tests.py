from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from graphql_jwt.testcases import JSONWebTokenTestCase
from graphql_relay.node.node import to_global_id

from .models import Item, Storage


class ModelTests(TestCase):
    fixtures = ['users', 'storage']

    def test_storage_str(self):
        storage = Storage.objects.get(pk=1)

        self.assertEqual(str(storage), '阳台')

    def test_item_str(self):
        item = Item.objects.get(pk=1)

        self.assertEqual(str(item), '雨伞')


class StorageModelTests(TestCase):
    fixtures = ['users', 'storage']

    def test_ancestors(self):
        """ 测试父节点 """
        balcony = Storage.objects.get(name="阳台")
        locker = Storage.objects.get(name="阳台储物柜")
        toolbox = Storage.objects.get(name="工具箱")
        toolbox2 = Storage.objects.get(name="工具箱2")

        self.assertEqual(balcony.parent, None)
        self.assertEqual(list(balcony.get_ancestors()), [])

        self.assertEqual(locker.parent, balcony)
        self.assertEqual(list(locker.get_ancestors()), [balcony])

        self.assertEqual(toolbox.parent, locker)
        self.assertEqual(list(toolbox.get_ancestors()), [balcony, locker])

    def test_children(self):
        balcony = Storage.objects.get(name="阳台")
        locker = Storage.objects.get(name="阳台储物柜")
        toolbox = Storage.objects.get(name="工具箱")
        toolbox2 = Storage.objects.get(name="工具箱2")

        self.assertEqual(list(balcony.get_children()), [locker])

        self.assertEqual(list(locker.get_children()), [toolbox, toolbox2])

        self.assertEqual(list(toolbox.get_children()), [])


class StorageTests(JSONWebTokenTestCase):
    fixtures = ['users', 'storage']

    def setUp(self):
        self.user = get_user_model().objects.get(username='test')
        self.client.authenticate(self.user)

    def test_get_storage(self):
        toolbox = Storage.objects.get(name='工具箱')

        query = '''
            query storage($id: ID!) {
                storage(id: $id) {
                    id
                    name
                    items {
                        edges {
                            node {
                                id
                                name
                            }
                        }
                    }
                }
            }
        '''
        variables = {'id': to_global_id('StorageType', toolbox.id)}

        content = self.client.execute(query, variables)
        self.assertIsNone(content.errors)

        name = content.data['storage']['name']
        self.assertEqual(name, toolbox.name)

    def test_get_storages(self):
        query = '''
            query storages {
                storages {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
        '''
        content = self.client.execute(query)
        self.assertIsNone(content.errors)

        names = [
            item['node']['name'] for item in content.data['storages']['edges']
        ]
        self.assertEqual(set(names), set(['阳台', '阳台储物柜', '工具箱', '工具箱2']))

    def test_get_root_storage(self):
        query = '''
            query storages {
                storages(level: 0) {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
        '''
        content = self.client.execute(query)
        self.assertIsNone(content.errors)

        names = [
            item['node']['name'] for item in content.data['storages']['edges']
        ]
        self.assertEqual(set(names), {'阳台'})

    def test_get_storage_ancestors(self):
        query = '''
            query storage($id: ID!)  {
                storage(id: $id) {
                    name
                    ancestors {
                        edges {
                            node {
                                name
                            }
                        }
                    }
                }
            }
        '''
        storage = Storage.objects.get(name='工具箱')
        variables = {'id': to_global_id('StorageType', storage.id)}

        content = self.client.execute(query, variables)
        self.assertIsNone(content.errors)

        self.assertEqual(content.data['storage']['name'], storage.name)
        names = [
            item['node']['name']
            for item in content.data['storage']['ancestors']['edges']
        ]
        self.assertEqual(names, ['阳台', '阳台储物柜'])

    def test_search(self):
        query = '''
            query search($key: String!) {
                storages(name_Icontains: $key) {
                    edges {
                        node {
                            name
                        }
                    }
                }
                items(name_Icontains: $key) {
                    edges {
                        node {
                            name
                        }
                    }
                }
            }
        '''
        variables = {'key': '口罩'}

        content = self.client.execute(query, variables)
        self.assertIsNone(content.errors)

        items = content.data['items']['edges']
        storages = content.data['storages']['edges']
        self.assertEqual([item['node']['name'] for item in items], ['口罩'])
        self.assertEqual(storages, [])

    def test_add_storage(self):
        mutation = '''
            mutation addStorage($input: AddStorageMutationInput!) {
                addStorage(input: $input) {
                    storage {
                        __typename
                        id
                        name
                        description
                        parent {
                            id
                        }
                    }
                }
            }
        '''
        variables = {
            'input': {
                'name': 'test',
                'description': 'some',
                'parentId': to_global_id('StorageType', '1')
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)

        storage = content.data['addStorage']['storage']
        self.assertEqual(storage['__typename'], 'StorageType')
        self.assertEqual(storage['name'], 'test')
        self.assertEqual(storage['description'], 'some')
        self.assertEqual(storage['parent']['id'],
                         to_global_id('StorageType', '1'))

    def test_delete_storage(self):
        mutation = '''
            mutation deleteStorage($input: DeleteStorageMutationInput!) {
                deleteStorage(input: $input) {
                    __typename
                }
            }
        '''

        toolbox = Storage.objects.get(name='工具箱')
        variables = {
            'input': {
                'storageId': to_global_id('StorageType', toolbox.id),
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)

        with self.assertRaises(Storage.DoesNotExist):
            Storage.objects.get(name='工具箱')

    def test_update_storage(self):
        mutation = '''
            mutation updateStorage($input: UpdateStorageMutationInput!) {
                updateStorage(input: $input) {
                    storage {
                        __typename
                        id
                        name
                        description
                        parent {
                            __typename
                            id
                            name
                        }
                    }
                }
            }
        '''
        variables = {
            'input': {
                'id': to_global_id('StorageType', '3'),
                'name': 'test',
                'description': 'some',
                'parentId': to_global_id('StorageType', '1')
            }
        }

        old_storage = Storage.objects.get(pk=3)
        self.assertEqual(old_storage.name, '工具箱')

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)

        storage = content.data['updateStorage']['storage']
        self.assertEqual(storage['__typename'], 'StorageType')
        self.assertEqual(storage['id'], to_global_id('StorageType', '3'))
        self.assertEqual(storage['name'], 'test')
        self.assertEqual(storage['description'], 'some')
        self.assertEqual(storage['parent']['id'],
                         to_global_id('StorageType', '1'))
        self.assertEqual(storage['parent']['name'], '阳台')

    def test_add_storage_name_duplicate(self):
        mutation = '''
            mutation addStorage($input: AddStorageMutationInput!) {
                addStorage(input: $input) {
                    storage {
                        name
                        description
                    }
                }
            }
        '''
        variables = {
            'input': {
                'name': '阳台',
                'description': 'some',
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '名称重复')

    def test_update_storage_name_duplicate(self):
        """ 测试修改名称重复 """
        mutation = '''
            mutation updateStorage($input: UpdateStorageMutationInput!) {
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
                'id': to_global_id('StorageType', '1'),
                'name': '阳台储物柜',
                'description': 'some',
            }
        }

        old_storage = Storage.objects.get(pk=1)
        self.assertEqual(old_storage.name, '阳台')

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '名称重复')

    def test_delete_storage_not_exist(self):
        mutation = '''
            mutation deleteStorage($input: DeleteStorageMutationInput!) {
                deleteStorage(input: $input) {
                    __typename
                }
            }
        '''
        variables = {
            'input': {
                'storageId': to_global_id('StorageType', '0'),
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '位置不存在，无法删除')


class ItemTests(JSONWebTokenTestCase):
    fixtures = ['users', 'storage']

    def setUp(self):
        self.user = get_user_model().objects.get(username='test')
        self.client.authenticate(self.user)

    def test_get_item(self):
        umbrella = Item.objects.get(name='雨伞')

        query = '''
            query item($id: ID!) {
                item(id: $id) {
                    id
                    name
                }
            }
        '''
        variables = {
            'id': to_global_id('ItemType', umbrella.id),
        }

        content = self.client.execute(query, variables)
        self.assertIsNone(content.errors)

        name = content.data['item']['name']
        self.assertEqual(name, umbrella.name)

    def test_get_items(self):
        query = '''
            query items {
                items {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
        '''
        content = self.client.execute(query)
        self.assertIsNone(content.errors)

        names = [
            item['node']['name'] for item in content.data['items']['edges']
        ]
        self.assertEqual(set(names), set(['雨伞', '口罩']))

    def test_get_recently_edited_items(self):
        query = '''
            query recentlyEditedItems  {
                items(orderBy: "-edited_at") {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
        '''
        content = self.client.execute(query)
        self.assertIsNone(content.errors)

        names = [
            item['node']['name'] for item in content.data['items']['edges']
        ]
        self.assertEqual(names, ['雨伞', '口罩'])

    def test_get_recently_added_items(self):
        query = '''
            query recentlyAddedItems {
                items(orderBy: "-created_at") {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
        '''
        content = self.client.execute(query)
        self.assertIsNone(content.errors)

        names = [
            item['node']['name'] for item in content.data['items']['edges']
        ]
        self.assertEqual(names, ['口罩', '雨伞'])

    def test_get_near_expired_items(self):
        query = '''
            query nearExpiredItems  {
                items(expiredAt_Gt: "2020-04-17T02:34:59.862Z") {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
        '''
        content = self.client.execute(query)
        self.assertIsNone(content.errors)

        items = content.data['items']['edges']
        self.assertEqual(items, [])

    def test_get_expired_items(self):
        query = '''
            query expiredItems  {
                items(expiredAt_Lt: "2020-03-01T00:00:00.000Z") {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
        '''
        content = self.client.execute(query)
        self.assertIsNone(content.errors)

        names = [
            item['node']['name'] for item in content.data['items']['edges']
        ]
        self.assertEqual(set(names), {'雨伞'})

    def test_add_item(self):
        mutation = '''
            mutation addItem($input: AddItemMutationInput!) {
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
                        expiredAt
                        editedAt
                        editedBy {
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
                'storageId': to_global_id('StorageType', '1'),
                'description': 'some',
                'price': 12.0,
                'expiredAt': None,
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
            mutation deleteItem($input: DeleteItemMutationInput!) {
                deleteItem(input: $input) {
                    __typename
                }
            }
        '''

        umbrella = Item.objects.get(name='雨伞')
        variables = {
            'input': {
                'itemId': to_global_id('ItemType', umbrella.id)
            },
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)

        deleted_umbrella = Item.objects.get(name='雨伞')
        self.assertEqual(deleted_umbrella.is_deleted, True)

    def test_update_item(self):
        mutation = '''
            mutation updateItem($input: UpdateItemMutationInput!) {
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
                        expiredAt
                        editedAt
                        editedBy {
                            username
                        }
                    }
                }
            }
        '''
        expiration_date = timezone.now()
        variables = {
            'input': {
                'id': to_global_id('ItemType', '1'),
                'name': 'test',
                'number': 2,
                'storageId': to_global_id('StorageType', '2'),
                'description': 'some',
                'price': 12.0,
                'expiredAt': expiration_date.isoformat(),
            }
        }

        old_item = Item.objects.get(pk=1)
        self.assertEqual(old_item.name, '雨伞')

        content = self.client.execute(mutation, variables)
        self.assertIsNone(content.errors)
        item = content.data['updateItem']['item']

        self.assertEqual(item['__typename'], 'ItemType')
        self.assertEqual(item['id'], to_global_id('ItemType', '1'))
        self.assertEqual(item['name'], 'test')
        self.assertEqual(item['number'], 2)
        self.assertEqual(item['description'], 'some')
        self.assertEqual(item['storage']['id'],
                         to_global_id('StorageType', '2'))
        self.assertEqual(item['price'], 12.0)
        self.assertEqual(item['expiredAt'], expiration_date.isoformat())

    def test_add_item_name_duplicate(self):
        mutation = '''
            mutation addItem($input: AddItemMutationInput!) {
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
                        expiredAt
                        editedAt
                        editedBy {
                            username
                        }
                    }
                }
            }
        '''
        variables = {
            'input': {
                'name': '雨伞',
                'number': 1,
                'storageId': to_global_id('StorageType', '1'),
                'description': 'some',
                'price': 12.0,
                'expiredAt': None,
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '名称重复')

    def test_update_item_name_duplicate(self):
        mutation = '''
            mutation updateItem($input: UpdateItemMutationInput!) {
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
                        expiredAt
                        editedAt
                        editedBy {
                            username
                        }
                    }
                }
            }
        '''
        variables = {
            'input': {
                'id': to_global_id('ItemType', '1'),
                'name': '口罩',
                'number': 2,
                'storageId': to_global_id('StorageType', '2')
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '名称重复')

    def test_delete_item_not_exist(self):
        mutation = '''
            mutation deleteItem($input: DeleteItemMutationInput!) {
                deleteItem(input: $input) {
                    __typename
                }
            }
        '''

        variables = {
            'input': {
                'itemId': to_global_id('ItemType', '0'),
            }
        }

        content = self.client.execute(mutation, variables)
        self.assertIsNotNone(content.errors)

        self.assertEqual(content.errors[0].message, '物品不存在')
