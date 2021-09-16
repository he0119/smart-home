# Generated by Django 3.1.4 on 2020-12-21 11:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def set_edited_by(apps, schema_editor):
    """将修改人设置为录入人"""
    Item = apps.get_model("storage", "Item")
    for item in Item.objects.all():
        item.edited_by = item.created_by
        item.save()


def reverse_set_edited_by(apps, schema_editor):
    """删除 storage_id 为空的物品"""
    Item = apps.get_model("storage", "Item")
    for item in Item.objects.filter(storage_id__isnull=True).all():
        item.delete()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("storage", "0002_item_date_added"),
    ]

    operations = [
        migrations.RenameField(
            model_name="item",
            old_name="date_added",
            new_name="created_at",
        ),
        migrations.RenameField(
            model_name="item",
            old_name="editor",
            new_name="created_by",
        ),
        migrations.RenameField(
            model_name="item",
            old_name="expiration_date",
            new_name="expired_at",
        ),
        migrations.RenameField(
            model_name="item",
            old_name="update_date",
            new_name="edited_at",
        ),
        migrations.AlterField(
            model_name="item",
            name="edited_at",
            field=models.DateTimeField(auto_now=True, verbose_name="修改时间"),
        ),
        migrations.AlterField(
            model_name="item",
            name="expired_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="有效日期"),
        ),
        migrations.AlterField(
            model_name="item",
            name="storage",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="items",
                to="storage.storage",
                verbose_name="属于",
            ),
        ),
        migrations.AlterField(
            model_name="item",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="created_items",
                to=settings.AUTH_USER_MODEL,
                verbose_name="录入人",
            ),
        ),
        migrations.AddField(
            model_name="item",
            name="edited_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="edited_items",
                to=settings.AUTH_USER_MODEL,
                verbose_name="修改人",
            ),
        ),
        migrations.AddField(
            model_name="item",
            name="deleted_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="删除时间"),
        ),
        migrations.AddField(
            model_name="item",
            name="is_deleted",
            field=models.BooleanField(default=False, verbose_name="逻辑删除"),
        ),
        # 临时取消自动设置为当前时间
        # 等待执行完脚本后恢复
        migrations.AlterField(
            model_name="item",
            name="edited_at",
            field=models.DateTimeField(verbose_name="修改时间"),
        ),
        migrations.RunPython(set_edited_by, reverse_code=reverse_set_edited_by),
        migrations.AlterField(
            model_name="item",
            name="edited_at",
            field=models.DateTimeField(auto_now=True, verbose_name="修改时间"),
        ),
    ]
