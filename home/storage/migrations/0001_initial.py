# Generated by Django 3.0.3 on 2020-02-25 17:13

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
            name='Storage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='名字')),
                ('description', models.CharField(blank=True, max_length=200, null=True, verbose_name='备注')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='storage.Storage', verbose_name='属于')),
            ],
            options={
                'verbose_name': '位置',
                'verbose_name_plural': '位置',
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='名字')),
                ('number', models.IntegerField(verbose_name='数量')),
                ('description', models.CharField(blank=True, max_length=200, null=True, verbose_name='备注')),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='价格')),
                ('update_date', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('expiration_date', models.DateTimeField(blank=True, null=True, verbose_name='有效期至')),
                ('editor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='录入者')),
                ('storage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='storage.Storage', verbose_name='属于')),
            ],
            options={
                'verbose_name': '物品',
                'verbose_name_plural': '物品',
                'ordering': ['name'],
            },
        ),
    ]