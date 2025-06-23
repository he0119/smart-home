"""用户相关的中间件

https://docs.djangoproject.com/zh-hans/4.0/topics/http/middleware/
"""

from importlib import import_module

from django.conf import settings
from django.contrib.sessions.middleware import (
    SessionMiddleware as BaseSessionMiddleware,
)


class SessionMiddleware(BaseSessionMiddleware):
    def __init__(self, get_response):
        super().__init__(get_response)
        engine = import_module(settings.SESSION_ENGINE)
        self.SessionStore = engine.SessionStore

    def process_request(self, request):
        session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
        # 获取代理下的客户端 IP 地址
        # https://django-user-sessions.readthedocs.io/en/stable/installation.html#ip-when-behind-a-proxy
        if "HTTP_X_FORWARDED_FOR" in request.META:
            request.META["REMOTE_ADDR"] = request.META["HTTP_X_FORWARDED_FOR"].split(",")[0].strip()
        request.session = self.SessionStore(
            ip=request.META.get("REMOTE_ADDR", ""),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            session_key=session_key,
        )
