import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Item


@csrf_exempt
def xiaoai(request):
    """ 小爱同学 """
    if request.method == 'POST':
        received_json_data = json.loads(request.body)
        response = process_request(received_json_data)
        return JsonResponse(response)

    return JsonResponse({'xiaoai': 'working'})


def process_request(data: dict) -> str:
    """ 处理小爱同学的请求 """
    print(data)
    slot_info = data['request']['slot_info']
    message = ''

    if slot_info['intent_name'] == 'find_item':
        message = find_item(slot_info['slots'][0]['value'])

    if not message:
        message = '对不起，我找不到'

    response = {
        'version': '1.0',
        'response': {
            'to_speak': {
                'type': 0,
                'text': message
            },
        },
        'is_session_end': True
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
        return f'找到{item_count}个物品{message}'

    return ''
