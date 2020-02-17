from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.datetime_safe import datetime

from .models import Item, Storage
from .forms import ItemForm, StorageForm


def index(request):
    storage_list = Storage.objects.filter(parent__isnull=True)
    storage_form = StorageForm()
    context = {
        'storage_list': storage_list,
        'storage_form': storage_form,
    }
    return render(request, 'storage/index.html', context)


def storage_detail(request, storage_id):
    storage = get_object_or_404(Storage, pk=storage_id)
    item_form = ItemForm(initial={
        'storage': storage,
        'update_date': datetime.now()
    })
    return render(request, 'storage/storage_detail.html', {
        'storage': storage,
        'item_form': item_form,
    })


def item_detail(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    return render(request, 'storage/item_detail.html', {'item': item})


def add_storage(request):
    try:
        storage = Storage.objects.get(name=request.POST['name'])
    except Storage.DoesNotExist:
        f = StorageForm(request.POST)
        new_storage = f.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(
            reverse('storage:storage_detail', args=(new_storage.id, )))
    else:
        return render(request, 'storage/storage_detail.html',
                      {'storage': storage})


def add_item(request, storage_id):
    storage = get_object_or_404(Storage, pk=storage_id)
    try:
        item = storage.item_set.get(name=request.POST['name'])
    except Item.DoesNotExist:
        f = ItemForm(request.POST)
        new_item = f.save(commit=False)
        new_item.update_date = datetime.now()
        new_item.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(
            reverse('storage:item_detail', args=(new_item.id, )))
    else:
        return render(request, 'storage/item_detail.html', {'item': item})
