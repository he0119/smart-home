from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from mptt.exceptions import InvalidMove

from .forms import ItemForm, StorageForm
from .models import Item, Storage


@login_required
def index(request):
    """ 主页 """
    storage_list = Storage.objects.filter(parent__isnull=True)
    form = StorageForm()
    context = {
        'storage_list': storage_list,
        'form': form,
    }
    return render(request, 'storage/index.html', context)


@login_required
def storage_detail(request, storage_id):
    """ 存储位置的详情页 """
    storage = get_object_or_404(Storage, pk=storage_id)

    item_form = ItemForm(initial={
        'number': 1,
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
            'parents': storage.get_ancestors(),
        })


@login_required
def item_detail(request, item_id):
    """ 物品的详情页 """
    item = get_object_or_404(Item, pk=item_id)
    return render(request, 'storage/item_detail.html', {'item': item})


@login_required
def add_storage(request):
    """ 存储位置的添加页 """
    if request.method == 'GET':
        form = StorageForm()
        return render(request, 'storage/add_storage.html', {'form': form})
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
    if request.method == 'GET':
        form = ItemForm(initial={
            'number': 1,
        })
        return render(request, 'storage/add_item.html', {'form': form})
    if request.method == 'POST':
        f = ItemForm(request.POST)
        new_item = f.save(commit=False)
        try:
            item = new_item.storage.item_set.get(name=new_item.name)
        except Item.DoesNotExist:
            new_item.update_date = timezone.now()
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
        storage = get_object_or_404(Storage, pk=storage_id)
        f = StorageForm(request.POST, instance=storage)
        try:
            storage = f.save()
        except InvalidMove:
            messages.add_message(request, messages.ERROR, '一个位置不能属于它的子节点')
            form = StorageForm(instance=storage)
            return render(request, 'storage/change_storage.html', {
                'storage': storage,
                'form': form,
            })
        return HttpResponseRedirect(
            reverse('storage:storage_detail', args=(storage.id, )))


@login_required
def change_item(request, item_id):
    """ 物品的修改页 """
    if request.method == 'GET':
        item = get_object_or_404(Item, pk=item_id)
        form = ItemForm(instance=item)
        return render(request, 'storage/change_item.html', {
            'item': item,
            'form': form,
        })
    if request.method == 'POST':
        item = get_object_or_404(Item, pk=item_id)
        f = ItemForm(request.POST, instance=item)
        item = f.save(commit=False)
        item.update_date = timezone.now()
        item.save()
        return HttpResponseRedirect(
            reverse('storage:item_detail', args=(item.id, )))


@login_required
def delete_storage(request, storage_id):
    """ 存储位置的删除页 """
    if request.method == 'GET':
        storage = get_object_or_404(Storage, pk=storage_id)
        return render(request, 'storage/delete_storage.html', {
            'storage': storage,
        })
    if request.method == 'POST':
        storage = get_object_or_404(Storage, pk=storage_id)
        if '_cancel' in request.POST:
            return HttpResponseRedirect(
                reverse('storage:storage_detail', args=(storage.id, )))
        if '_confirm' in request.POST:
            parent = storage.parent
            storage.delete()
            if parent:
                return HttpResponseRedirect(
                    reverse('storage:storage_detail', args=(parent.id, )))
            return HttpResponseRedirect(reverse('storage:index'))


@login_required
def delete_item(request, item_id):
    """ 物品的删除页 """
    if request.method == 'GET':
        item = get_object_or_404(Item, pk=item_id)
        return render(request, 'storage/delete_item.html', {
            'item': item,
        })
    if request.method == 'POST':
        item = get_object_or_404(Item, pk=item_id)
        if '_cancel' in request.POST:
            return HttpResponseRedirect(
                reverse('storage:item_detail', args=(item.id, )))
        if '_confirm' in request.POST:
            storage = item.storage
            item.delete()
            return HttpResponseRedirect(
                reverse('storage:storage_detail', args=(storage.id, )))


@login_required
def search(request):
    if request.method == 'GET':
        search_query = request.GET.get('q', None)
        storages = Storage.objects.filter(name__contains=search_query)
        items = Item.objects.filter(name__contains=search_query)
        total = len(storages) + len(items)
        return render(request, 'storage/search.html', {
            'storages': storages,
            'items': items,
            'total': total,
        })
