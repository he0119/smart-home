# Generated by Django 3.1.4 on 2020-12-23 11:08

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("board", "0002_add_is_pin"),
    ]

    operations = [
        migrations.RenameField(
            model_name="comment",
            old_name="date_created",
            new_name="created_at",
        ),
        migrations.RenameField(
            model_name="comment",
            old_name="date_modified",
            new_name="edited_at",
        ),
        migrations.RenameField(
            model_name="topic",
            old_name="date_created",
            new_name="created_at",
        ),
        migrations.RenameField(
            model_name="topic",
            old_name="date_modified",
            new_name="edited_at",
        ),
    ]
