from celery import shared_task
from django.core import management


@shared_task
def clear_sessions():
    """清除过期的会话"""
    management.call_command("clearsessions")
