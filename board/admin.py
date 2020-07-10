from django.contrib import admin
from django.contrib.auth import get_user_model
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from import_export.resources import ModelResource
from import_export.widgets import ForeignKeyWidget

from .models import Comment, Topic


class TopicResource(ModelResource):
    user = Field(column_name='user',
                 attribute='user',
                 widget=ForeignKeyWidget(get_user_model(), 'username'))

    class Meta:
        model = Topic
        export_order = (
            'id',
            'title',
            'description',
            'user',
            'date_created',
            'date_modified',
        )
        skip_unchanged = True
        report_skipped = False


class CommentResource(ModelResource):
    user = Field(column_name='user',
                 attribute='user',
                 widget=ForeignKeyWidget(get_user_model(), 'username'))

    reply_to = Field(column_name='reply_to',
                     attribute='reply_to',
                     widget=ForeignKeyWidget(get_user_model(), 'username'))

    class Meta:
        model = Comment
        exclude = (
            'lft',
            'rght',
            'tree_id',
            'level',
        )
        export_order = (
            'id',
            'topic',
            'user',
            'reply_to',
            'body',
            'date_created',
            'date_modified',
            'parent',
        )
        skip_unchanged = True
        report_skipped = False


class TopicAdmin(ImportExportModelAdmin):
    resource_class = TopicResource
    list_display = ('title', 'description', 'user')


class CommentAdmin(ImportExportModelAdmin):
    resource_class = CommentResource
    list_display = ('topic', 'user', 'body', 'reply_to')


admin.site.register(Topic, TopicAdmin)
admin.site.register(Comment, CommentAdmin)
