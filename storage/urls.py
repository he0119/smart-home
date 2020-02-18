from django.urls import path

from . import views

app_name = 'storage'
urlpatterns = [
    path('', views.index, name='index'),
    path('storage/add', views.add_storage, name='add_storage'),
    path('storage/<int:storage_id>/',
         views.storage_detail,
         name='storage_detail'),
    path('storage/<int:storage_id>/delete',
         views.delete_storage,
         name='delete_storage'),
    path('item/add', views.add_item, name='add_item'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('item/<int:item_id>/delete', views.delete_item, name='delete_item'),
]
