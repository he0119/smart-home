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
def add_storage(request):
    f = StorageForm(request.POST)
    new_storage = f.save(commit=False)
    try:
        storage = Storage.objects.get(name=new_storage.name)
    except Storage.DoesNotExist:
        new_storage.save()
        if new_storage.parent:
            return HttpResponseRedirect(
                reverse('storage:storage_detail',
                        args=(new_storage.parent.id, )))
        return HttpResponseRedirect(reverse('storage:index'))
    else:
        return HttpResponseRedirect(
            reverse('storage:storage_detail', args=(storage.id, )))


@login_required
def add_item(request):
    if request.method == 'POST':
        f = ItemForm(request.POST)
        new_item = f.save(commit=False)
        try:
            item = new_item.storage.item_set.get(name=new_item.name)
        except Item.DoesNotExist:
            new_item.update_date = datetime.now()
            new_item.save()
            return HttpResponseRedirect(
                reverse('storage:storage_detail', args=(new_item.storage.id, )))
        else:
            return HttpResponseRedirect(
                reverse('storage:item_detail', args=(item.id, )))


@login_required
def delete_storage(request, storage_id):
    storage = get_object_or_404(Storage, pk=storage)
    parent = storage.parent
    storage.delete()
    return HttpResponseRedirect(
        reverse('storage:storage_detail', args=(parent.id, )))


@login_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    storage = item.storage
    item.delete()
    return HttpResponseRedirect(
        reverse('storage:storage_detail', args=(storage.id, )))
