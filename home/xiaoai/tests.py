import json

from django.test import TestCase
from django.test.client import RequestFactory
from django.urls import reverse

from .views import is_xiaomi, xiaomi_hmac


def get_command_data(name: str, intent_name: str = "find_item") -> str:
    """生成小爱同学的命令"""
    data = {
        "version": "1.0",
        "session": {
            "is_new": False,
            "session_id": "",
            "application": {"app_id": ""},
            "user": {"user_id": "", "is_user_login": True, "gender": "unknown"},
            "attributes": {},
        },
        "request": {
            "type": 1,
            "request_id": "",
            "timestamp": 1607403502306,
            "intent": {
                "query": f"{name}在哪？",
                "score": 0.800000011920929,
                "complete": True,
                "domain": "openplatform",
                "confidence": 1,
                "skillType": "Custom",
                "sub_domain": "",
                "app_id": "",
                "request_type": "Intent",
                "need_fetch_token": False,
                "is_direct_wakeup": False,
                "slots": {
                    "intent_name": "find_item",
                    "slots": [{"name": "item", "value": name, "raw_value": name}],
                },
            },
            "locale": "zh-CN",
            "slot_info": {
                "intent_name": intent_name,
                "slots": [{"name": "item", "value": name, "raw_value": name}],
            },
            "is_monitor": True,
        },
        "query": f"{name}在哪？",
        "context": {
            "device_id": "",
            "user_agent": "",
            "device_category": "soundbox",
            "in_exp": False,
        },
    }
    return json.dumps(data)


class XiaoaiTest(TestCase):
    fixtures = ["users", "storage"]

    def setUp(self) -> None:
        self.headers = {
            "HTTP_Authorization": "MIAI-HmacSHA256-V1 key_id::f117594ae9af4bf5bdc1319972c7b2bb310fd0022ea8da52114c430e2b68218b",
            "HTTP_X-Xiaomi-Date": "Tue, 8 Dec 2020 03:26:17 GMT",
            "HTTP_Host": "smart-test.hehome.xyz",
            "HTTP_Content-Type": "application/json",
            "HTTP_Content-Md5": "Content-Md5",
        }

    def test_xiaoai_get(self):
        """测试小爱是否正常运行"""
        response = self.client.get(reverse("xiaoai:xiaoai"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"xiaoai": "working"})

    def test_xiaoai_post_without_sign(self):
        """测试未签名的情况"""
        response = self.client.post(
            reverse("xiaoai:xiaoai"),
            data=get_command_data("口罩"),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)

    def test_xiaoai_post(self):
        """测试获取物品信息"""
        response = self.client.post(
            reverse("xiaoai:xiaoai"),
            data=get_command_data("口罩"),
            content_type="application/json",
            **self.headers,  # type: ignore
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "version": "1.0",
                "response": {
                    "to_speak": {
                        "type": 0,
                        "text": "共找到1个物品，口罩在阳台储物柜。",
                    },
                    "not_understand": False,
                },
                "is_session_end": True,
            },
        )

    def test_xiaoai_post_item_not_exist(self):
        """测试获取不存在的物品信息"""
        response = self.client.post(
            reverse("xiaoai:xiaoai"),
            data=get_command_data("手机"),
            content_type="application/json",
            **self.headers,  # type: ignore
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "version": "1.0",
                "response": {
                    "to_speak": {"type": 0, "text": "找不到名字是手机的物品。"},
                    "not_understand": False,
                },
                "is_session_end": True,
            },
        )

    def test_xiaoai_post_different_intent(self):
        """测试其他意图"""
        response = self.client.post(
            reverse("xiaoai:xiaoai"),
            data=get_command_data("手机", "test"),
            content_type="application/json",
            **self.headers,  # type: ignore
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "version": "1.0",
                "response": {
                    "to_speak": {"type": 0, "text": "对不起，我没有理解到你的意思。"},
                    "not_understand": True,
                },
                "is_session_end": False,
            },
        )

    def test_xiaomi_hmac(self):
        """测试签名"""
        headers = {
            "X-Xiaomi-Date": "Tue, 8 Dec 2020 03:26:17 GMT",
            "Host": "smart-test.hehome.xyz",
            "Content-Type": "application/json",
            "Content-Md5": "Content-Md5",
        }
        signature = "2ba08b462b8409d51131c661e23609d7575d3fa584713b0e52e9d4d651b0e3c9"

        request = RequestFactory().post("/xiaoai", headers=headers)
        self.assertEqual(xiaomi_hmac(request), signature)

    def test_is_xiaomi(self):
        """测试判断是否为小米服务器发出的请求"""
        headers = {
            "Authorization": "MIAI-HmacSHA256-V1 key_id::2ba08b462b8409d51131c661e23609d7575d3fa584713b0e52e9d4d651b0e3c9",
            "X-Xiaomi-Date": "Tue, 8 Dec 2020 03:26:17 GMT",
            "Host": "smart-test.hehome.xyz",
            "Content-Type": "application/json",
            "Content-Md5": "Content-Md5",
        }
        request = RequestFactory().post("/xiaoai", headers=headers)
        self.assertEqual(is_xiaomi(request), True)

        headers = {
            "Authorization": "MIAI-HmacSHA256-V1 key_id::f117594ae9af4bf5bdc1319972c7b2bb310fd0022ea8da52114c430e2b68218b",
            "X-Xiaomi-Date": "Tue, 8 Dec 2020 03:26:17 GMT",
            "Host": "smart-test.hehome.xyz",
            "Content-Type": "application/json",
            "Content-Md5": "Content-Md5",
        }
        request = RequestFactory().post("/api/xiaoai/", headers=headers)
        self.assertEqual(is_xiaomi(request), True)

    def test_wrong_sign_method(self):
        """测试签名方式版本不正确的情况"""
        headers = {
            "Authorization": "Wrong key_id::2ba08b462b8409d51131c661e23609d7575d3fa584713b0e52e9d4d651b0e3c9",
            "X-Xiaomi-Date": "Tue, 8 Dec 2020 03:26:17 GMT",
            "Host": "smart-test.hehome.xyz",
            "Content-Type": "application/json",
            "Content-Md5": "Content-Md5",
        }

        request = RequestFactory().post("/xiaoai", headers=headers)
        self.assertEqual(is_xiaomi(request), False)

    def test_wrong_key_id(self):
        """测试密钥ID不正确的情况"""
        headers = {
            "Authorization": "MIAI-HmacSHA256-V1 wrong_id::2ba08b462b8409d51131c661e23609d7575d3fa584713b0e52e9d4d651b0e3c9",
            "X-Xiaomi-Date": "Tue, 8 Dec 2020 03:26:17 GMT",
            "Host": "smart-test.hehome.xyz",
            "Content-Type": "application/json",
            "Content-Md5": "Content-Md5",
        }

        request = RequestFactory().post("/xiaoai", headers=headers)
        self.assertEqual(is_xiaomi(request), False)

    def test_wrong_signature(self):
        """测试签名不正确的情况"""
        headers = {
            "Authorization": "MIAI-HmacSHA256-V1 key_id::wrong_signature",
            "X-Xiaomi-Date": "Tue, 8 Dec 2020 03:26:17 GMT",
            "Host": "smart-test.hehome.xyz",
            "Content-Type": "application/json",
            "Content-Md5": "Content-Md5",
        }

        request = RequestFactory().post("/xiaoai", headers=headers)
        self.assertEqual(is_xiaomi(request), False)
