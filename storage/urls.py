from django.urls import path

from . import views

app_name = 'storage'
urlpatterns = [
    path('', views.index, name='index'),
    path('storage/<int:storage_id>/', views.storage_detail, name='storage_detail'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
]
