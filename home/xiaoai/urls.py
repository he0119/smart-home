from django.urls import path

from . import views

app_name = "xiaoai"
urlpatterns = [
    path("", views.xiaoai, name="xiaoai"),
]
