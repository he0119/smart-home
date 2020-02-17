from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Storage, Item


def index(request):
    storage_list = Storage.objects.filter(parent__isnull=True)
    context = {
        'storage_list': storage_list,
    }
    return render(request, 'storage/index.html', context)


def storage_detail(request, storage_id):
    storage = get_object_or_404(Storage, pk=storage_id)
    return render(request, 'storage/storage_detail.html', {'storage': storage})


def item_detail(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    return render(request, 'storage/item_detail.html', {'item': item})
