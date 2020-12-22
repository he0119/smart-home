from celery import shared_task
from django.core import management


@shared_task
def clear_expired_tokens():
    """ 清楚过期的令牌 """
    management.call_command('cleartokens', expired=True)
