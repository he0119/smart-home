# Generated by Django 3.0.3 on 2020-03-24 05:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='标题')),
                ('description', models.TextField(verbose_name='说明')),
                ('is_open', models.BooleanField(verbose_name='进行中')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='发布时间')),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topics', to=settings.AUTH_USER_MODEL, verbose_name='创建者')),
            ],
            options={
                'verbose_name': '话题',
                'verbose_name_plural': '话题',
                'ordering': ['date_created'],
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField(verbose_name='内容')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='发布时间')),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='board.Comment', verbose_name='属于')),
                ('reply_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='repliers', to=settings.AUTH_USER_MODEL, verbose_name='回复给')),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='board.Topic', verbose_name='话题')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='评论者')),
            ],
            options={
                'verbose_name': '评论',
                'verbose_name_plural': '评论',
            },
        ),
    ]
