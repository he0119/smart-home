from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:storage_id>/', views.storage_detail, name='storage_detail'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
]
