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
        form = StorageForm(request.POST)
        try:
            storage = Storage.objects.get(name=form.data['storage-name'])
        except Storage.DoesNotExist:
            if form.is_valid():
                new_storage = form.save()
                messages.info(request, f'位置 {new_storage.name} 添加完成')
                if new_storage.parent:
                    return HttpResponseRedirect(
                        reverse('storage:storage_detail',
                                args=(new_storage.parent.id, )))
                return HttpResponseRedirect(reverse('storage:index'))
            else:
                render(request, 'storage/add_storage.html', {'form': form})
        else:
            messages.info(request, f'位置 {storage.name} 已存在，自动转跳至该位置详情页面')
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
        form = ItemForm(request.POST)
        # 检查是否已经有同名物品，如有则自动转跳
        try:
            item = Item.objects.get(name=form.data['item-name'])
        except Item.DoesNotExist:
            if form.is_valid():
                new_item = form.save(commit=False)
                new_item.update_date = timezone.now()
                new_item.editor = request.user
                new_item.save()
                messages.info(request, f'物品 {new_item.name} 添加完成')
                return HttpResponseRedirect(
                    reverse('storage:storage_detail',
                            args=(new_item.storage.id, )))
            else:
                return render(request, 'storage/add_item.html', {'form': form})
        else:
            messages.info(request, f'物品 {item.name} 已存在，自动转跳至该物品详情页面')
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
        form = StorageForm(request.POST, instance=storage)
        if form.is_valid():
            try:
                storage = form.save()
            except InvalidMove:
                messages.error(request, '一个位置不能属于它自己或其子节点')
                return render(request, 'storage/change_storage.html', {
                    'storage': storage,
                    'form': form,
                })
            else:
                messages.info(request, f'位置 {storage.name} 修改成功')
                return HttpResponseRedirect(
                    reverse('storage:storage_detail', args=(storage.id, )))
        else:
            return render(request, 'storage/change_storage.html', {
                'storage': storage,
                'form': form,
            })


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
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save(commit=False)
            item.update_date = timezone.now()
            item.editor = request.user
            item.save()
            messages.info(request, f'物品 {item.name} 修改成功')
        else:
            return render(request, 'storage/change_item.html', {
                'item': item,
                'form': form,
            })
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
            messages.info(request, f'位置 {storage.name} 删除成功')
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
            messages.info(request, f'物品 {item.name} 删除成功')
            item.delete()
            return HttpResponseRedirect(
                reverse('storage:storage_detail', args=(storage.id, )))


@login_required
def search(request):
    if request.method == 'GET':
        search_query = request.GET.get('q', None)
        items = (Item.objects.filter(name__icontains=search_query)
                 | Item.objects.filter(
                     description__icontains=search_query)).distinct()
        storages = (Storage.objects.filter(name__icontains=search_query)
                    | Storage.objects.filter(
                        description__icontains=search_query)).distinct()
        total = len(items) + len(storages)
        return render(request, 'storage/search.html', {
            'total': total,
            'items': items,
            'storages': storages,
        })


@login_required
def latest(request):
    if request.method == 'GET':
        items = Item.objects.all().order_by('-update_date')[:50]
        return render(request, 'storage/latest.html', {
            'items': items,
        })
