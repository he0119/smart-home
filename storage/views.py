import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Item


@csrf_exempt
def xiaoai(request):
    """ 小爱同学 """
    print(request.headers['Authorization'])
    if request.method == 'POST':
        received_json_data = json.loads(request.body)
        response = process_request(received_json_data)
        return JsonResponse(response)

    return JsonResponse({'xiaoai': 'working'})


def process_request(data: dict) -> str:
    """ 处理小爱同学发来的请求

    暂时只支持查询物品的位置
    """
    print(data)
    message = ''
    is_session_end = True

    slot_info = data['request']['slot_info']
    # 查询物品位置
    if slot_info['intent_name'] == 'find_item':
        message = find_item(slot_info['slots'][0]['value'])

    if not message:
        message = '对不起，我没有理解到你的意思。'
        is_session_end = False

    # 构造小米支持的格式
    # 语音回复
    response = {
        'version': '1.0',
        'response': {
            'to_speak': {
                'type': 0,
                'text': message
            },
        },
        'is_session_end': is_session_end
    }

    return response


def find_item(name: str) -> str:
    """ 查找物品 """
    items = Item.objects.filter(name__icontains=name)
    item_count = len(items)

    if item_count > 0:
        message = ''
        for item in items:
            message += f'，{item.name}在{item.storage.name}'
        return f'共找到{item_count}个物品{message}。'

    return f'找不到名字是{name}的物品。'
