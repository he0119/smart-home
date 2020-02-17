from django.http import HttpResponse


def index(request):
    return HttpResponse("欢迎来到物品管理页面。")
