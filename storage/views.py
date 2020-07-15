from .models import Storage
from django.core import serializers
from django.http import JsonResponse


def xiaoai(request):
    """ 小爱同学 """
    some_data_to_dump = {
        'some_var_1': 'foo',
        'some_var_2': 'bar',
    }

    return JsonResponse(some_data_to_dump)
