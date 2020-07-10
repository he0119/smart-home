from django.conf import settings
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class Topic(models.Model):
    """ 话题 """
    class Meta:
        verbose_name = '话题'
        verbose_name_plural = '话题'
        ordering = ['date_created']

    title = models.CharField(max_length=200, verbose_name='标题')
    description = models.TextField(verbose_name='说明')
    is_open = models.BooleanField(verbose_name='进行中')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='topics',
                             verbose_name='创建者')
    date_created = models.DateTimeField(auto_now_add=True, verbose_name='发布时间')
    date_modified = models.DateTimeField(auto_now=True, verbose_name='修改时间')

    def __str__(self):
        return self.title


class Comment(MPTTModel):
    """ 评论 """
    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'

    topic = models.ForeignKey(Topic,
                              on_delete=models.CASCADE,
                              related_name='comments',
                              verbose_name='话题')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='comments',
                             verbose_name='评论者')
    body = models.TextField(verbose_name='内容')
    date_created = models.DateTimeField(auto_now_add=True, verbose_name='发布时间')
    date_modified = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    parent = TreeForeignKey('self',
                            on_delete=models.CASCADE,
                            null=True,
                            blank=True,
                            related_name='children',
                            verbose_name='属于')
    reply_to = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 null=True,
                                 blank=True,
                                 on_delete=models.SET_NULL,
                                 related_name='repliers',
                                 verbose_name='回复给')

    def __str__(self):
        return self.body[:20]
