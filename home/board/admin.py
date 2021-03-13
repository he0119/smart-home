from django.contrib import admin

from .models import Comment, Topic


class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'user', 'created_at')
    search_fields = ['title', 'description']


class CommentAdmin(admin.ModelAdmin):
    list_filter = ('topic', )
    list_display = ('topic', 'user', 'body', 'reply_to', 'created_at')
    search_fields = ['body']


admin.site.register(Topic, TopicAdmin)
admin.site.register(Comment, CommentAdmin)
