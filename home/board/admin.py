from django.contrib import admin

from .models import Comment, Topic


class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'user')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('topic', 'user', 'body', 'reply_to')


admin.site.register(Topic, TopicAdmin)
admin.site.register(Comment, CommentAdmin)
