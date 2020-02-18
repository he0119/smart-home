from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.datetime_safe import datetime

from .forms import ItemForm, StorageForm
from .models import Item, Storage


@login_required
def index(request):
    storage_list = Storage.objects.filter(parent__isnull=True)
    storage_form = StorageForm()
    context = {
        'storage_list': storage_list,
        'storage_form': storage_form,
    }
    return render(request, 'storage/index.html', context)


@login_required
def storage_detail(request, storage_id):
    storage = get_object_or_404(Storage, pk=storage_id)

    # 获取存储位置的上一级
    parents = []
    parent = storage.parent
    while parent:
        parents.append(parent)
        parent = parent.parent
    parents.reverse()

    item_form = ItemForm(initial={
        'storage': storage,
    })
    storage_form = StorageForm(initial={
        'parent': storage,
    })
    return render(
        request, 'storage/storage_detail.html', {
            'storage': storage,
            'item_form': item_form,
            'storage_form': storage_form,
            'parents': parents,
        })


@login_required
def item_detail(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    return render(request, 'storage/item_detail.html', {'item': item})


@login_required
def add_storage(request, storage_id):
    try:
        storage = Storage.objects.get(name=request.POST['name'])
    except Storage.DoesNotExist:
        f = StorageForm(request.POST)
        new_storage = f.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        if storage_id == 0:
            return HttpResponseRedirect(reverse('storage:index'))
        return HttpResponseRedirect(
            reverse('storage:storage_detail', args=(storage_id, )))
    else:
        return render(request, 'storage/storage_detail.html',
                      {'storage': storage})


@login_required
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
            reverse('storage:storage_detail', args=(storage.id, )))
    else:
        return render(request, 'storage/item_detail.html', {'item': item})
