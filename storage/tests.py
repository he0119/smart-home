from django.test import TestCase

from .models import Storage


def query_set_to_list(query_set):
    """ 转换 TreeQuerySet 到列表 """
    new = []
    for i in query_set:
        new.append(i)
    return new


class StorageModelTests(TestCase):
    def setUp(self):
        balcony = Storage.objects.create(name="阳台", description='家里的阳台')
        locker = Storage.objects.create(name="阳台储物柜", parent=balcony)
        toolbox = Storage.objects.create(name="工具箱", parent=locker)
        toolbox2 = Storage.objects.create(name="工具箱2", parent=locker)

    def test_ancestors(self):
        """ 测试父节点 """
        balcony = Storage.objects.get(name="阳台")
        locker = Storage.objects.get(name="阳台储物柜")
        toolbox = Storage.objects.get(name="工具箱")
        toolbox2 = Storage.objects.get(name="工具箱2")

        self.assertEqual(balcony.parent, None)
        self.assertEqual(query_set_to_list(balcony.get_ancestors()), [])
        self.assertEqual(query_set_to_list(balcony.get_children()), [locker])

        self.assertEqual(locker.parent, balcony)
        self.assertEqual(query_set_to_list(locker.get_ancestors()), [balcony])
        self.assertEqual(query_set_to_list(locker.get_children()),
                         [toolbox, toolbox2])

        self.assertEqual(toolbox.parent, locker)
        self.assertEqual(query_set_to_list(toolbox.get_ancestors()),
                         [balcony, locker])
