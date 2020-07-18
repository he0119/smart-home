from django.http import JsonResponse
from .api import AutowateringAPI


def iot(request):
    """ 物联网 """
    api = AutowateringAPI('1')
    return JsonResponse(api.set_status(key='valve1', value=True))
