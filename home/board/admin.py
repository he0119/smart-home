from django.contrib import admin

from .models import Comment, Topic


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "user", "created_at")
    search_fields = ["title", "description"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_filter = ("topic",)
    list_display = ("topic", "user", "body", "reply_to", "created_at")
    search_fields = ["body"]
