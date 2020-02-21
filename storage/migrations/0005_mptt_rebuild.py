# 重建树

from django.db import migrations
from mptt import managers, register


def rebuild_tree(apps, schema_editor):
    Storage = apps.get_model('storage', 'Storage')

    manager = managers.TreeManager()
    manager.model = Storage

    register(Storage)

    manager.contribute_to_class(Storage, 'objects')
    manager.rebuild()


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0004_mptt'),
    ]

    operations = [
        migrations.RunPython(rebuild_tree),
    ]
