# Generated by Django 3.1.4 on 2020-12-25 02:53

from django.db import migrations, models


def set_edited_at(apps, schema_editor):
    """修改话题的时间

    将关闭话题的修改时间设置成创建时间
    将其关闭时间设置成其修改时间
    将置顶话题的修改时间设置成创建时间
    """
    Topic = apps.get_model("board", "Topic")
    for topic in Topic.objects.all():
        if not topic.is_open:
            topic.edited_at = topic.created_at
            topic.closed_at = topic.edited_at
            topic.save()
        if topic.is_pin:
            topic.edited_at = topic.created_at
            topic.save()


def reverse_set_edited_at(apps, schema_editor):
    """不做任何事情"""
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("board", "0003_rename_field"),
    ]

    operations = [
        migrations.AddField(
            model_name="topic",
            name="closed_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="关闭时间"),
        ),
        migrations.AlterField(
            model_name="topic",
            name="edited_at",
            field=models.DateTimeField(verbose_name="修改时间"),
        ),
        migrations.RunPython(set_edited_at, reverse_code=reverse_set_edited_at),
    ]
