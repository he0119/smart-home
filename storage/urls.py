from django.urls import path

from . import views

app_name = 'storage'
urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('storage/add/', views.add_storage, name='add_storage'),
    path('storage/<int:storage_id>/',
         views.storage_detail,
         name='storage_detail'),
    path('storage/<int:storage_id>/change',
         views.change_storage,
         name='change_storage'),
    path('storage/<int:storage_id>/delete/',
         views.delete_storage,
         name='delete_storage'),
    path('item/add', views.add_item, name='add_item'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('item/<int:item_id>/change/', views.change_item, name='change_item'),
    path('item/<int:item_id>/delete/', views.delete_item, name='delete_item'),
]
