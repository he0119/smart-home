from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.datetime_safe import datetime

from .forms import ItemForm, StorageForm
from .models import Item, Storage


@login_required
def index(request):
    """ 主页 """
    storage_list = Storage.objects.filter(parent__isnull=True)
    storage_form = StorageForm()
    context = {
        'storage_list': storage_list,
        'storage_form': storage_form,
    }
    return render(request, 'storage/index.html', context)


@login_required
def storage_detail(request, storage_id):
    """ 存储位置的详情页 """
    storage = get_object_or_404(Storage, pk=storage_id)

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
            'parents': storage.parents(),
        })


@login_required
def item_detail(request, item_id):
    """ 物品的详情页 """
    item = get_object_or_404(Item, pk=item_id)
    return render(request, 'storage/item_detail.html', {'item': item})


@login_required
def add_storage(request):
    """ 存储位置的添加页 """
    if request.method == 'POST':
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
    """ 物品的添加页 """
    if request.method == 'POST':
        f = ItemForm(request.POST)
        new_item = f.save(commit=False)
        try:
            item = new_item.storage.item_set.get(name=new_item.name)
        except Item.DoesNotExist:
            new_item.update_date = datetime.now()
            new_item.save()
            return HttpResponseRedirect(
                reverse('storage:storage_detail',
                        args=(new_item.storage.id, )))
        else:
            return HttpResponseRedirect(
                reverse('storage:item_detail', args=(item.id, )))


@login_required
def change_storage(request, storage_id):
    """ 存储位置的修改页 """
    if request.method == 'GET':
        storage = get_object_or_404(Storage, pk=storage_id)
        form = StorageForm(instance=storage)
        return render(request, 'storage/change_storage.html', {
            'storage': storage,
            'form': form,
        })
    if request.method == 'POST':
        pass


@login_required
def change_item(request):
    """ 物品的修改页 """
    pass


@login_required
def delete_storage(request, storage_id):
    """ 存储位置的删除页 """
    if request.method == 'POST':
        storage = get_object_or_404(Storage, pk=storage_id)
        parent = storage.parent
        storage.delete()
        return HttpResponseRedirect(
            reverse('storage:storage_detail', args=(parent.id, )))


@login_required
def delete_item(request, item_id):
    """ 物品的删除页 """
    if request.method == 'POST':
        item = get_object_or_404(Item, pk=item_id)
        storage = item.storage
        item.delete()
        return HttpResponseRedirect(
            reverse('storage:storage_detail', args=(storage.id, )))
