from django.test import TestCase

from .models import Storage


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

        self.assertEqual(balcony.parent, None)
        self.assertEqual(len(balcony.get_ancestors()), 0)
        self.assertEqual(len(balcony.get_children()), 1)

        self.assertEqual(locker.parent, balcony)
        self.assertEqual(len(locker.get_ancestors()), 1)
        self.assertEqual(len(locker.get_children()), 2)

        self.assertEqual(toolbox.parent, locker)
        self.assertEqual(len(toolbox.get_ancestors()), 2)
