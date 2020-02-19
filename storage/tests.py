from django.test import TestCase

from .models import Storage


class StorageModelTests(TestCase):
    def setUp(self):
        balcony = Storage.objects.create(name="阳台", description='家里的阳台')
        locker = Storage.objects.create(name="阳台储物柜", parent=balcony)
        toolbox = Storage.objects.create(name="工具箱", parent=locker)

    def test_parents(self):
        """ 测试父节点 """
        balcony = Storage.objects.get(name="阳台")
        locker = Storage.objects.get(name="阳台储物柜")
        toolbox = Storage.objects.get(name="工具箱")

        self.assertEqual(balcony.parent, None)
        self.assertEqual(balcony.parents(), [])

        self.assertEqual(locker.parent, balcony)
        self.assertEqual(locker.parents(), [balcony])

        self.assertEqual(toolbox.parent, locker)
        self.assertEqual(toolbox.parents(), [balcony, locker])
