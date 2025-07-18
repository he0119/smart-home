import base64
import json
import logging
from hashlib import sha256
from hmac import HMAC

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from home.storage.models import Item

# Get an instance of a logger
logger = logging.getLogger("xiaoai")


@csrf_exempt
def xiaoai(request):
    """小爱同学"""
    if request.method == "POST":
        if is_xiaomi(request):
            received_json_data = json.loads(request.body)
            response = process_request(received_json_data)
            return JsonResponse(response)
        else:
            return HttpResponse(status=401)

    return JsonResponse({"xiaoai": "working"})


def process_request(data: dict) -> dict:
    """处理小爱同学发来的请求

    暂时只支持查询物品的位置
    """
    logger.info(data)
    message = ""
    not_understand = False
    is_session_end = True

    slot_info = data["request"]["slot_info"]
    # 查询物品位置
    if slot_info["intent_name"] == "find_item":
        message = find_item(slot_info["slots"][0]["value"])

    if not message:
        message = "对不起，我没有理解到你的意思。"
        not_understand = True
        is_session_end = False

    # 构造小米支持的格式
    # 语音回复
    response = {
        "version": "1.0",
        "response": {
            "to_speak": {"type": 0, "text": message},
            "not_understand": not_understand,
        },
        "is_session_end": is_session_end,
    }

    return response


def find_item(name: str) -> str:
    """查找物品"""
    items = Item.objects.filter(name__icontains=name)
    item_count = len(items)

    if item_count > 0:
        message = ""
        for item in items:
            if item.storage is not None:
                message += f"，{item.name}在{item.storage.name}"
        return f"共找到{item_count}个物品{message}。"

    return f"找不到名字是{name}的物品。"


def xiaomi_hmac(request):
    """小米签名

    MIAI-HmacSHA256-V1
    """
    headers = request.headers
    secret = settings.XIAOAI_SECRET
    method = request.method
    url_path = request.path
    param = ""
    xiaomi_date = headers["X-Xiaomi-Date"]
    host = headers["Host"]
    content_type = headers["Content-Type"]
    md5 = headers["Content-Md5"]
    # 拼接签名字符串，最后一行是空行
    source = "\n".join([method, url_path, param, xiaomi_date, host, content_type, md5, ""])
    signature = HMAC(base64.b64decode(secret), source.encode("utf8"), sha256).digest().hex()
    return signature


def is_xiaomi(request) -> bool:
    """是否是小米发送的请求"""
    try:
        headers = request.headers
        authorization = headers["Authorization"]
        sign_version = authorization.split()[0]
        key_id, scope, signature = authorization.split()[1].split(":")
        if sign_version == "MIAI-HmacSHA256-V1":
            if key_id != settings.XIAOAI_KEY_ID:
                return False
            if signature != xiaomi_hmac(request):
                return False
            return True
        else:
            return False
    except Exception:
        return False
