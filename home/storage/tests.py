from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from strawberry_django_plus.gql import relay

from home.tests import GraphQLTestCase

from . import types
from .models import Item, Picture, Storage


class ModelTests(TestCase):
    fixtures = ["users", "storage"]

    def test_storage_str(self):
        storage = Storage.objects.get(pk=1)

        self.assertEqual(str(storage), "阳台")

    def test_item_str(self):
        item = Item.objects.get(pk=1)

        self.assertEqual(str(item), "雨伞")

    def test_picture_str(self):
        picture = Picture.objects.get(pk=1)

        self.assertEqual(str(picture), "测试一")


class StorageModelTests(TestCase):
    fixtures = ["users", "storage"]

    def test_ancestors(self):
        """测试父节点"""
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


class StorageTests(GraphQLTestCase):
    fixtures = ["users", "storage"]

    def setUp(self):
        self.user = get_user_model().objects.get(username="test")
        self.client.authenticate(self.user)

    def test_get_storage(self):
        storage = Storage.objects.get(name="阳台储物柜")

        query = """
            query storage($id: GlobalID!) {
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
        """
        variables = {"id": relay.to_base64(types.Storage, storage.id)}

        content = self.client.execute(query, variables)

        name = content.data["storage"]["name"]
        self.assertEqual(name, storage.name)
        item = content.data["storage"]["items"]["edges"][1]["node"]
        self.assertEqual(item["name"], "垃圾")

    def test_get_storage_connection_filter(self):
        """测试位置下的 Connection 能否使用 filter"""
        storage = Storage.objects.get(name="阳台储物柜")

        query = """
            query storage($id: GlobalID!) {
                storage(id: $id) {
                    id
                    name
                    items(filters: {}, order: {}) {
                        edges {
                            node {
                                id
                                name
                            }
                        }
                    }
                    children(filters: {}) {
                        edges {
                            node {
                                id
                                name
                            }
                        }
                    }
                    ancestors(filters: {}) {
                        edges {
                            node {
                                id
                                name
                            }
                        }
                    }
                }
            }
        """
        variables = {"id": relay.to_base64(types.Storage, storage.id)}

        content = self.client.execute(query, variables)

        name = content.data["storage"]["name"]
        self.assertEqual(name, storage.name)
        item = content.data["storage"]["items"]["edges"][1]["node"]
        self.assertEqual(item["name"], "手表")

    def test_get_storages(self):
        query = """
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
        """
        content = self.client.execute(query)

        names = [item["node"]["name"] for item in content.data["storages"]["edges"]]
        self.assertEqual(set(names), {"阳台", "阳台储物柜", "工具箱", "工具箱2"})

    def test_get_root_storage(self):
        """测试获取根节点"""
        query = """
            query storages {
                storages(filters: {level: {exact: 0}}) {
                    edges {
                        node {
                            id
                            name
                            parent {
                                id
                            }
                        }
                    }
                }
            }
        """
        content = self.client.execute(query)

        names = [item["node"]["name"] for item in content.data["storages"]["edges"]]
        self.assertEqual(set(names), {"阳台"})

    def test_get_storage_ancestors(self):
        query = """
            query storage($id: GlobalID!)  {
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
        """
        storage = Storage.objects.get(name="工具箱")
        variables = {"id": relay.to_base64(types.Storage, storage.id)}

        content = self.client.execute(query, variables)

        self.assertEqual(content.data["storage"]["name"], storage.name)
        names = [
            item["node"]["name"]
            for item in content.data["storage"]["ancestors"]["edges"]
        ]
        self.assertEqual(names, ["阳台", "阳台储物柜"])

    def test_search(self):
        query = """
            query search($key: String!) {
                storages(filters: {name: {contains: $key}}) {
                    edges {
                        node {
                            name
                        }
                    }
                }
                items(filters: {name: {contains: $key}}) {
                    edges {
                        node {
                            name
                        }
                    }
                }
            }
        """
        variables = {"key": "口罩"}

        content = self.client.execute(query, variables)

        items = content.data["items"]["edges"]
        storages = content.data["storages"]["edges"]
        self.assertEqual([item["node"]["name"] for item in items], ["口罩"])
        self.assertEqual(storages, [])

    def test_add_storage(self):
        """添加位置"""
        mutation = """
            mutation addStorage($input: AddStorageInput!) {
                addStorage(input: $input) {
                    ... on Storage {
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
        """
        variables = {
            "input": {
                "name": "test",
                "description": "some",
                "parentId": relay.to_base64(types.Storage, 1),
            }
        }

        content = self.client.execute(mutation, variables)

        storage = content.data["addStorage"]
        self.assertEqual(storage["__typename"], "Storage")
        self.assertEqual(storage["name"], "test")
        self.assertEqual(storage["description"], "some")
        self.assertEqual(storage["parent"]["id"], relay.to_base64(types.Storage, 1))

    def test_delete_storage(self):
        """删除位置"""
        mutation = """
            mutation deleteStorage($input: DeleteStorageInput!) {
                deleteStorage(input: $input) {
                    ... on Storage {
                        __typename
                    }
                }
            }
        """

        toolbox = Storage.objects.get(name="工具箱")
        variables = {
            "input": {
                "storageId": relay.to_base64(types.Storage, toolbox.id),
            }
        }

        self.client.execute(mutation, variables)

        with self.assertRaises(Storage.DoesNotExist):
            Storage.objects.get(name="工具箱")

    def test_update_storage(self):
        """更新位置"""
        old_storage = Storage.objects.get(pk=3)
        self.assertEqual(old_storage.id, 3)
        self.assertEqual(old_storage.name, "工具箱")
        self.assertEqual(old_storage.description, "")
        self.assertEqual(old_storage.parent_id, 2)

        mutation = """
            mutation updateStorage($input: UpdateStorageInput!) {
                updateStorage(input: $input) {
                    ... on Storage {
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
        """
        variables = {
            "input": {
                "id": relay.to_base64(types.Storage, old_storage.id),
                "name": "test",
                "description": "some",
                "parentId": relay.to_base64(types.Storage, 1),
            }
        }

        content = self.client.execute(mutation, variables)

        storage = content.data["updateStorage"]
        self.assertEqual(storage["__typename"], "Storage")
        self.assertEqual(storage["id"], relay.to_base64(types.Storage, "3"))
        self.assertEqual(storage["name"], "test")
        self.assertEqual(storage["description"], "some")
        self.assertEqual(storage["parent"]["id"], relay.to_base64(types.Storage, 1))

    def test_add_storage_name_duplicate(self):
        """添加相同名称的位置"""
        old_storage = Storage.objects.get(pk=1)

        mutation = """
            mutation addStorage($input: AddStorageInput!) {
                addStorage(input: $input) {
                    ... on Storage {
                        __typename
                        id
                        name
                    }
                }
            }
        """
        variables = {
            "input": {
                "name": old_storage.name,
            }
        }

        content = self.client.execute(mutation, variables)

        storage = content.data["addStorage"]
        self.assertEqual(storage["__typename"], "Storage")
        self.assertNotEqual(
            storage["id"], relay.to_base64(types.Storage, old_storage.id)
        )
        self.assertEqual(storage["name"], old_storage.name)

    def test_update_storage_name_duplicate(self):
        """更新位置名称为已有名称"""
        old_storage = Storage.objects.get(pk=2)
        self.assertEqual(old_storage.name, "阳台储物柜")

        mutation = """
            mutation updateStorage($input: UpdateStorageInput!) {
                updateStorage(input: $input) {
                    ... on Storage {
                        __typename
                        id
                        name
                    }
                }
            }
        """
        variables = {
            "input": {
                "id": relay.to_base64(types.Storage, 1),
                "name": old_storage.name,
            }
        }

        content = self.client.execute(mutation, variables)

        storage = content.data["updateStorage"]
        self.assertEqual(storage["__typename"], "Storage")
        self.assertNotEqual(
            storage["id"], relay.to_base64(types.Storage, old_storage.id)
        )
        self.assertEqual(storage["name"], old_storage.name)

    def test_update_storage_not_exist(self):
        mutation = """
            mutation updateStorage($input: UpdateStorageInput!) {
                updateStorage(input: $input) {
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
                "id": relay.to_base64(types.Storage, "0"),
                "name": "阳台储物柜",
                "description": "some",
            }
        }

        old_storage = Storage.objects.get(pk=1)
        self.assertEqual(old_storage.name, "阳台")

        content = self.client.execute(mutation, variables)

        data = content.data["updateStorage"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "无法修改不存在的位置")

    def test_update_storage_root(self):
        """测试修改位置至根节点

        即 parentId 为 None
        """
        mutation = """
            mutation updateStorage($input: UpdateStorageInput!) {
                updateStorage(input: $input) {
                    ... on Storage {
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
        """
        variables = {
            "input": {
                "id": relay.to_base64(types.Storage, "3"),
                "name": "test",
                "description": "some",
                "parentId": None,
            }
        }

        old_storage = Storage.objects.get(pk=3)
        self.assertEqual(old_storage.name, "工具箱")

        content = self.client.execute(mutation, variables)

        storage = content.data["updateStorage"]
        self.assertEqual(storage["__typename"], "Storage")
        self.assertEqual(storage["id"], relay.to_base64(types.Storage, "3"))
        self.assertEqual(storage["name"], "test")
        self.assertEqual(storage["description"], "some")
        self.assertEqual(storage["parent"], None)

    def test_delete_storage_not_exist(self):
        mutation = """
            mutation deleteStorage($input: DeleteStorageInput!) {
                deleteStorage(input: $input) {
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
                "storageId": relay.to_base64(types.Storage, "0"),
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["deleteStorage"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "无法删除不存在的位置")

    def test_add_storage_parent_not_exist(self):
        mutation = """
            mutation addStorage($input: AddStorageInput!) {
                addStorage(input: $input) {
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
                "name": "test",
                "description": "some",
                "parentId": relay.to_base64(types.Storage, "0"),
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["addStorage"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "上一级位置不存在")

    def test_update_storage_parent_not_exist(self):
        mutation = """
            mutation updateStorage($input: UpdateStorageInput!) {
                updateStorage(input: $input) {
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
                "id": relay.to_base64(types.Storage, 1),
                "parentId": relay.to_base64(types.Storage, "0"),
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["updateStorage"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "上一级位置不存在")


class ItemTests(GraphQLTestCase):
    fixtures = ["users", "storage"]

    def setUp(self):
        self.user = get_user_model().objects.get(username="test")
        self.client.authenticate(self.user)

    def test_get_item(self):
        umbrella = Item.objects.get(name="雨伞")

        query = """
            query item($id: GlobalID!) {
                item(id: $id) {
                    id
                    name
                    pictures {
                        edges {
                            node {
                                description
                            }
                        }
                    }
                }
            }
        """
        variables = {
            "id": relay.to_base64(types.Item, umbrella.id),
        }

        content = self.client.execute(query, variables)

        name = content.data["item"]["name"]
        self.assertEqual(name, umbrella.name)
        item = content.data["item"]["pictures"]["edges"][0]["node"]
        self.assertEqual(item["description"], "测试一")

    def test_get_item_missing_storage(self):
        """获取没有位置的物品"""
        missing = Item.objects.get(name="未分类")

        query = """
            query item($id: GlobalID!) {
                item(id: $id) {
                    id
                    name
                    storage {
                        id
                        name
                    }
                }
            }
        """
        variables = {
            "id": relay.to_base64(types.Item, missing.id),
        }

        content = self.client.execute(query, variables)

        item = content.data["item"]
        self.assertEqual(item["name"], missing.name)
        self.assertIsNone(item["storage"])

    def test_item_connection_filter(self):
        umbrella = Item.objects.get(name="雨伞")

        query = """
            query item($id: GlobalID!) {
                item(id: $id) {
                    id
                    name
                    pictures(filters: {description: {exact: "测试二"}}, order: {}) {
                        edges {
                            node {
                                description
                            }
                        }
                    }
                    consumables(filters: {}, order: {}) {
                        edges {
                            node {
                                description
                            }
                        }
                    }
                }
            }
        """
        variables = {
            "id": relay.to_base64(types.Item, umbrella.id),
        }

        content = self.client.execute(query, variables)

        name = content.data["item"]["name"]
        self.assertEqual(name, umbrella.name)
        item = content.data["item"]["pictures"]["edges"][0]["node"]
        self.assertEqual(item["description"], "测试二")

    def test_get_items(self):
        query = """
            query items {
                items(filters: {}) {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
        """
        content = self.client.execute(query)

        self.assertEqual(len(content.data["items"]["edges"]), 5)

    def test_get_deleted_items(self):
        """测试获取已删除的物品"""
        query = """
            query items {
                items(filters: {isDeleted: true}) {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
        """
        content = self.client.execute(query)

        self.assertEqual(len(content.data["items"]["edges"]), 1)
        self.assertEqual(content.data["items"]["edges"][0]["node"]["name"], "垃圾")

    def test_get_missing_storage_items(self):
        """获取没有存放位置的物品"""
        query = """
            query items {
                items(filters: {storage: {isNull: true}}) {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
        """
        content = self.client.execute(query)

        self.assertEqual(len(content.data["items"]["edges"]), 1)
        self.assertEqual(content.data["items"]["edges"][0]["node"]["name"], "未分类")

    def test_get_recently_edited_items(self):
        query = """
            query recentlyEditedItems  {
                items(first: 2, order: {editedAt: DESC}) {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
        """
        content = self.client.execute(query)

        names = [item["node"]["name"] for item in content.data["items"]["edges"]]
        self.assertEqual(names, ["雨伞", "口罩"])

    def test_get_recently_added_items(self):
        query = """
            query recentlyAddedItems {
                items(first: 2, order: {createdAt: DESC}) {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
        """
        content = self.client.execute(query)

        names = [item["node"]["name"] for item in content.data["items"]["edges"]]
        self.assertEqual(names, ["口罩", "雨伞"])

    def test_get_near_expired_items(self):
        query = """
            query nearExpiredItems  {
                items(filters: {expiredAt: {gt: "2020-04-17T02:34:59.862Z"}}) {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
        """
        content = self.client.execute(query)

        items = content.data["items"]["edges"]
        self.assertEqual(items, [])

    def test_get_expired_items(self):
        query = """
            query expiredItems  {
                items(filters: {expiredAt: {lt: "2020-03-01T00:00:00.000Z"}}) {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
        """
        content = self.client.execute(query)

        names = [item["node"]["name"] for item in content.data["items"]["edges"]]
        self.assertEqual(set(names), {"雨伞"})

    def test_add_item(self):
        """添加物品"""
        mutation = """
            mutation addItem($input: AddItemInput!) {
                addItem(input: $input) {
                    ... on Item {
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
        """
        variables = {
            "input": {
                "name": "test",
                "number": 1,
                "storageId": relay.to_base64(types.Storage, 1),
                "description": "some",
                "price": 12.0,
                "expiredAt": None,
            }
        }

        content = self.client.execute(mutation, variables)

        item = content.data["addItem"]
        self.assertEqual(item["__typename"], "Item")
        self.assertEqual(item["name"], "test")
        self.assertEqual(item["description"], "some")
        self.assertEqual(item["number"], 1)
        self.assertEqual(item["storage"]["id"], relay.to_base64(types.Storage, "1"))
        self.assertEqual(item["price"], 12.0)
        self.assertEqual(item["expiredAt"], None)

    def test_delete_item(self):
        """删除物品"""
        mutation = """
            mutation deleteItem($input: DeleteItemInput!) {
                deleteItem(input: $input) {
                    __typename
                }
            }
        """

        umbrella = Item.objects.get(name="雨伞")
        variables = {
            "input": {"itemId": relay.to_base64(types.Item, umbrella.id)},
        }

        self.client.execute(mutation, variables)

        deleted_umbrella = Item.objects.get(name="雨伞")
        self.assertEqual(deleted_umbrella.is_deleted, True)

    def test_restore_item(self):
        """恢复物品"""
        mutation = """
            mutation restoreItem($input: RestoreItemInput!) {
                restoreItem(input: $input) {
                    __typename
                }
            }
        """

        umbrella = Item.objects.get(name="雨伞")
        variables = {
            "input": {"itemId": relay.to_base64(types.Item, umbrella.id)},
        }

        self.client.execute(mutation, variables)

        restore_umbrella = Item.objects.get(name="雨伞")
        self.assertEqual(restore_umbrella.is_deleted, False)

    def test_update_item(self):
        """更新物品"""
        old_item = Item.objects.get(pk=1)
        self.assertEqual(old_item.name, "雨伞")
        self.assertEqual(old_item.number, 1)
        self.assertEqual(old_item.description, "")

        mutation = """
            mutation updateItem($input: UpdateItemInput!) {
                updateItem(input: $input) {
                    ... on Item {
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
        """
        expiration_date = timezone.now()
        variables = {
            "input": {
                "id": relay.to_base64(types.Item, old_item.id),
                "name": "test",
                "number": 2,
                "storageId": relay.to_base64(types.Storage, "2"),
                "description": "some",
                "price": 12.0,
                "expiredAt": expiration_date.isoformat(),
            }
        }

        content = self.client.execute(mutation, variables)
        item = content.data["updateItem"]

        self.assertEqual(item["__typename"], "Item")
        self.assertEqual(item["id"], relay.to_base64(types.Item, "1"))
        self.assertEqual(item["name"], "test")
        self.assertEqual(item["number"], 2)
        self.assertEqual(item["description"], "some")
        self.assertEqual(item["storage"]["id"], relay.to_base64(types.Storage, "2"))
        self.assertEqual(item["price"], 12.0)
        self.assertEqual(item["expiredAt"], expiration_date.isoformat())

    def test_update_deleted_item(self):
        """测试修改已删除的物品"""
        mutation = """
            mutation updateItem($input: UpdateItemInput!) {
                updateItem(input: $input) {
                    ... on Item {
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
                        isDeleted
                    }
                }
            }
        """
        expiration_date = timezone.now()
        variables = {
            "input": {
                "id": relay.to_base64(types.Item, "5"),
                "name": "test",
                "number": 2,
                "storageId": relay.to_base64(types.Storage, "2"),
                "description": "some",
                "price": 12.0,
                "expiredAt": expiration_date.isoformat(),
            }
        }

        old_item = Item.objects.get(pk=5)
        self.assertEqual(old_item.name, "垃圾")
        self.assertEqual(old_item.is_deleted, True)

        content = self.client.execute(mutation, variables)
        item = content.data["updateItem"]

        self.assertEqual(item["__typename"], "Item")
        self.assertEqual(item["id"], relay.to_base64(types.Item, "5"))
        self.assertEqual(item["name"], "test")
        self.assertEqual(item["number"], 2)
        self.assertEqual(item["description"], "some")
        self.assertEqual(item["storage"]["id"], relay.to_base64(types.Storage, "2"))
        self.assertEqual(item["price"], 12.0)
        self.assertEqual(item["expiredAt"], expiration_date.isoformat())
        self.assertEqual(item["isDeleted"], False)

    def test_add_item_name_duplicate(self):
        """添加相同名称的物品"""
        mutation = """
            mutation addItem($input: AddItemInput!) {
                addItem(input: $input) {
                    ... on Item {
                        __typename
                        id
                        name
                        number
                        description
                        storage {
                            id
                        }
                    }
                }
            }
        """
        variables = {
            "input": {
                "name": "雨伞",
                "number": 1,
                "storageId": relay.to_base64(types.Storage, 1),
                "description": "some",
            }
        }

        content = self.client.execute(mutation, variables)

        item = content.data["addItem"]
        self.assertEqual(item["__typename"], "Item")
        self.assertEqual(item["name"], "雨伞")
        self.assertEqual(item["number"], 1)
        self.assertEqual(item["description"], "some")
        self.assertEqual(item["storage"]["id"], relay.to_base64(types.Storage, 1))

    def test_update_item_name_duplicate(self):
        """更新物品名称为已存在的名称"""
        mutation = """
            mutation updateItem($input: UpdateItemInput!) {
                updateItem(input: $input) {
                    ... on Item {
                        __typename
                        id
                        name
                    }
                }
            }
        """
        variables = {
            "input": {
                "id": relay.to_base64(types.Item, "1"),
                "name": "口罩",
            }
        }

        content = self.client.execute(mutation, variables)

        item = content.data["updateItem"]
        self.assertEqual(item["__typename"], "Item")
        self.assertEqual(item["name"], "口罩")

    def test_delete_item_not_exist(self):
        mutation = """
            mutation deleteItem($input: DeleteItemInput!) {
                deleteItem(input: $input) {
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
                "itemId": relay.to_base64(types.Item, "0"),
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["deleteItem"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "无法删除不存在的物品")

    def test_restore_item_not_exist(self):
        mutation = """
            mutation restoreItem($input: RestoreItemInput!) {
                restoreItem(input: $input) {
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
            "input": {"itemId": relay.to_base64(types.Item, "0")},
        }

        content = self.client.execute(mutation, variables)

        data = content.data["restoreItem"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "物品不存在")

    def test_update_item_not_exist(self):
        mutation = """
            mutation updateItem($input: UpdateItemInput!) {
                updateItem(input: $input) {
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
                "id": relay.to_base64(types.Item, "0"),
                "storageId": relay.to_base64(types.Storage, "2"),
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["updateItem"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "无法修改不存在的物品")

    def test_add_item_storage_not_exist(self):
        mutation = """
            mutation addItem($input: AddItemInput!) {
                addItem(input: $input) {
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
                "name": "test",
                "number": 1,
                "description": "",
                "storageId": relay.to_base64(types.Storage, "0"),
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["addItem"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "位置不存在")

    def test_update_item_storage_not_exist(self):
        mutation = """
            mutation updateItem($input: UpdateItemInput!) {
                updateItem(input: $input) {
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
                "id": relay.to_base64(types.Item, "1"),
                "storageId": relay.to_base64(types.Storage, "0"),
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["updateItem"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "位置不存在")


class ConsumableTests(GraphQLTestCase):
    """耗材相关的测试"""

    fixtures = ["users", "storage"]

    def setUp(self):
        self.user = get_user_model().objects.get(username="test")
        self.client.authenticate(self.user)

    def test_get_consumable(self):
        """获取设置了耗材的物品，与其耗材"""
        query = """
            query consumable {
                items(filters: {consumables: true}) {
                    edges {
                        node {
                            name
                            consumables {
                                edges {
                                    node {
                                       name
                                    }
                                }
                            }
                        }
                    }
                }
            }
        """
        content = self.client.execute(query)

        names = [item["node"]["name"] for item in content.data["items"]["edges"]]
        self.assertEqual(set(names), {"手表"})

        names = [
            item["node"]["name"]
            for item in content.data["items"]["edges"][0]["node"]["consumables"][
                "edges"
            ]
        ]
        self.assertEqual(set(names), {"电池"})

    def test_get_consumable_is_empty(self):
        """获取没有设置耗材的物品"""
        query = """
            query consumable {
                items(filters: {consumables: false}) {
                    edges {
                        node {
                            name
                            consumables {
                                edges {
                                    node {
                                       name
                                    }
                                }
                            }
                        }
                    }
                }
            }
        """
        content = self.client.execute(query)

        names = [item["node"]["name"] for item in content.data["items"]["edges"]]
        self.assertCountEqual(names, ["电池", "口罩", "雨伞", "未分类"])

    def test_get_consumable_is_null(self):
        """consumables 参数为 null 时，默认获取所有物品"""
        query = """
            query consumable {
                items(filters: {consumables: null}) {
                    edges {
                        node {
                            name
                            consumables {
                                edges {
                                    node {
                                       name
                                    }
                                }
                            }
                        }
                    }
                }
            }
        """
        content = self.client.execute(query)

        names = [item["node"]["name"] for item in content.data["items"]["edges"]]
        self.assertCountEqual(names, ["电池", "口罩", "雨伞", "手表", "未分类"])

    def test_add_consumable(self):
        """添加耗材"""
        mutation = """
            mutation addConsumable($input: AddConsumableInput!) {
                addConsumable(input: $input) {
                    ... on Item {
                        id
                        consumables {
                            edges {
                                node {
                                    name
                                }
                            }
                        }
                    }
                }
            }
        """
        variables = {
            "input": {
                "id": relay.to_base64(types.Item, "1"),
                "consumableIds": [relay.to_base64(types.Item, "2")],
            }
        }

        content = self.client.execute(mutation, variables)

        names = [
            item["node"]["name"]
            for item in content.data["addConsumable"]["consumables"]["edges"]
        ]
        self.assertEqual(set(names), {"口罩"})

    def test_error_add_consumable_item_not_exist(self):
        """物品不存在的情况"""
        mutation = """
            mutation addConsumable($input: AddConsumableInput!) {
                addConsumable(input: $input) {
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
                "id": relay.to_base64(types.Item, "0"),
                "consumableIds": [relay.to_base64(types.Item, "1")],
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["addConsumable"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "无法修改不存在的物品")

    def test_error_add_consumable_not_exist(self):
        """耗材不存在的情况"""
        mutation = """
            mutation addConsumable($input: AddConsumableInput!) {
                addConsumable(input: $input) {
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
                "id": relay.to_base64(types.Item, "1"),
                "consumableIds": [relay.to_base64(types.Item, "0")],
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["addConsumable"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "耗材不存在")

    def test_error_add_consumable_self(self):
        """耗材是自己的情况"""
        mutation = """
            mutation addConsumable($input: AddConsumableInput!) {
                addConsumable(input: $input) {
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
                "id": relay.to_base64(types.Item, "1"),
                "consumableIds": [relay.to_base64(types.Item, "1")],
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["addConsumable"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "不能添加自己作为自己的耗材")

    def test_delete_consumable(self):
        """删除耗材"""
        mutation = """
            mutation deleteConsumable($input: DeleteConsumableInput!) {
                deleteConsumable(input: $input) {
                    ... on Item {
                        id
                        consumables {
                            edges {
                                node {
                                    name
                                }
                            }
                        }
                    }
                }
            }
        """
        variables = {
            "input": {
                "id": relay.to_base64(types.Item, "3"),
                "consumableIds": [relay.to_base64(types.Item, "4")],
            }
        }

        item = Item.objects.get(pk="3")
        consumable = Item.objects.get(pk="4")
        self.assertCountEqual(item.consumables.all(), [consumable])

        content = self.client.execute(mutation, variables)

        names = [
            item["node"]["name"]
            for item in content.data["deleteConsumable"]["consumables"]["edges"]
        ]
        self.assertCountEqual(names, [])

    def test_error_delete_consumable_item_not_exist(self):
        """物品不存在的情况"""
        mutation = """
            mutation deleteConsumable($input: DeleteConsumableInput!) {
                deleteConsumable(input: $input) {
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
                "id": relay.to_base64(types.Item, "0"),
                "consumableIds": [relay.to_base64(types.Item, "1")],
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["deleteConsumable"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "无法修改不存在的物品")

    def test_error_delete_consumable_not_exist(self):
        """耗材不存在的情况"""
        mutation = """
            mutation deleteConsumable($input: DeleteConsumableInput!) {
                deleteConsumable(input: $input) {
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
                "id": relay.to_base64(types.Item, "1"),
                "consumableIds": [relay.to_base64(types.Item, "0")],
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["deleteConsumable"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "耗材不存在")


class PictureTests(GraphQLTestCase):
    fixtures = ["users", "storage"]

    def setUp(self):
        self.user = get_user_model().objects.get(username="test")
        self.client.authenticate(self.user)

    def test_get_picture(self):
        query = """
            query picture($id: GlobalID!) {
                picture(id: $id) {
                    __typename
                    id
                    name
                    url
                }
            }
        """
        variables = {
            "id": relay.to_base64(types.Picture, "1"),
        }

        content = self.client.execute(query, variables)

        picture = content.data["picture"]
        self.assertEqual(picture["name"], "1-0f5faff6-38f9-426a-b790-79630739b956.jpg")
        self.assertEqual(
            picture["url"], "/item_pictures/1-0f5faff6-38f9-426a-b790-79630739b956.jpg"
        )

    def test_get_pictures(self):
        query = """
            query pictures($itemName: String!) {
              pictures(
                filters: {item: {name: {exact: $itemName}}}
                order: {createdAt: DESC}
              ) {
                edges {
                  node {
                    id
                    item {
                      id
                      name
                    }
                    description
                    url
                  }
                }
              }
            }
        """
        variables = {
            "itemName": "雨伞",
        }

        content = self.client.execute(query, variables)

        picture = content.data["pictures"]["edges"][0]["node"]
        self.assertEqual(picture["description"], "测试二")
        self.assertEqual(
            picture["url"], "/item_pictures/1-57f3cd93-f838-4281-9bd8-18e64aa7b3dd.jpg"
        )

    def test_get_item_pictures(self):
        umbrella = Item.objects.get(name="雨伞")

        query = """
            query item($id: GlobalID!) {
                item(id: $id) {
                    id
                    name
                    pictures {
                        edges {
                            node {
                                name
                                url
                            }
                        }
                    }
                }
            }
        """
        variables = {
            "id": relay.to_base64(types.Item, umbrella.id),
        }

        content = self.client.execute(query, variables)

        name = content.data["item"]["name"]
        self.assertEqual(name, umbrella.name)
        picture = content.data["item"]["pictures"]["edges"][0]["node"]
        self.assertEqual(picture["name"], "1-0f5faff6-38f9-426a-b790-79630739b956.jpg")
        self.assertEqual(
            picture["url"], "/item_pictures/1-0f5faff6-38f9-426a-b790-79630739b956.jpg"
        )

    def test_add_picture(self):
        test_file = SimpleUploadedFile(name="test.txt", content=b"file_text")

        mutation = """
            mutation addPicture($input: AddPictureInput!) {
                addPicture(input: $input) {
                    ... on Picture {
                        __typename
                        id
                        description
                        item {
                            id
                        }
                        name
                        url
                        boxX
                        boxY
                        boxH
                        boxW
                    }
                }
            }
        """
        variables = {
            "input": {
                "file": None,
                "itemId": relay.to_base64(types.Item, "1"),
                "description": "test",
                "boxX": 0.1,
                "boxY": 0.1,
                "boxH": 0.1,
                "boxW": 0.1,
            }
        }

        content = self.client.execute(mutation, variables, files={"input": test_file})

        picture = content.data["addPicture"]
        self.assertEqual(picture["__typename"], "Picture")
        self.assertEqual(picture["description"], "test")

    def test_add_picture_not_exist(self):
        test_file = SimpleUploadedFile(name="test.txt", content=b"file_text")

        mutation = """
            mutation addPicture($input: AddPictureInput!) {
                addPicture(input: $input) {
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
                "file": None,
                "itemId": relay.to_base64(types.Item, "0"),
                "description": "test",
                "boxX": 0.1,
                "boxY": 0.1,
                "boxH": 0.1,
                "boxW": 0.1,
            }
        }

        content = self.client.execute(mutation, variables, files={"input": test_file})

        data = content.data["addPicture"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "无法给不存在的物品添加图片")

    def test_delete_picture(self):
        mutation = """
            mutation deletePicture($input: DeletePictureInput!) {
                deletePicture(input: $input) {
                    ... on Picture {
                        __typename
                    }
                }
            }
        """

        picture = Picture.objects.get(pk=1)
        variables = {
            "input": {"pictureId": relay.to_base64(types.Picture, picture.id)},
        }

        content = self.client.execute(mutation, variables)

        with self.assertRaises(Picture.DoesNotExist):
            Picture.objects.get(pk=1)

    def test_delete_picture_not_exist(self):
        mutation = """
            mutation deletePicture($input: DeletePictureInput!) {
                deletePicture(input: $input) {
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
            "input": {"pictureId": relay.to_base64(types.Picture, "0")},
        }

        content = self.client.execute(mutation, variables)

        data = content.data["deletePicture"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "无法删除不存在的图片")

    def test_update_picture(self):
        test_file = SimpleUploadedFile(name="test.txt", content=b"file_text")

        mutation = """
            mutation updatePicture($input: UpdatePictureInput!) {
                updatePicture(input: $input) {
                    ... on Picture {
                        __typename
                        id
                        description
                        item {
                            id
                        }
                        name
                        url
                        boxX
                        boxY
                        boxH
                        boxW
                    }
                }
            }
        """

        variables = {
            "input": {
                # 如果要测试文件的话，需要把文件放在第一位
                "file": None,
                "id": relay.to_base64(types.Picture, "1"),
                "description": "test",
                "boxX": 0.1,
                "boxY": 0.2,
                "boxH": 0.3,
                "boxW": 0.4,
            }
        }

        content = self.client.execute(mutation, variables, files={"input": test_file})

        picture = content.data["updatePicture"]
        self.assertEqual(picture["__typename"], "Picture")
        self.assertEqual(picture["description"], "test")
        self.assertEqual(picture["boxX"], 0.1)
        self.assertEqual(picture["boxY"], 0.2)
        self.assertEqual(picture["boxH"], 0.3)
        self.assertEqual(picture["boxW"], 0.4)

    def test_update_picture_not_exist(self):
        mutation = """
            mutation updatePicture($input: UpdatePictureInput!) {
                updatePicture(input: $input) {
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
                "id": relay.to_base64(types.Picture, "0"),
                "description": "test",
                "boxX": 0.1,
                "boxY": 0.1,
                "boxH": 0.1,
                "boxW": 0.1,
            }
        }

        content = self.client.execute(mutation, variables)

        data = content.data["updatePicture"]
        self.assertEqual(data["__typename"], "OperationInfo")
        self.assertEqual(data["messages"][0]["message"], "无法修改不存在的图片")
