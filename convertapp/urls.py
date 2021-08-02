from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [

    path('', views.home, name="home"),
    path('upload_client', views.upload_client, name="upload_client"),
    path('upload_sanveo', views.upload_sanveo, name="upload_sanveo"),
    path('processs', views.processs, name="processs"),
    path('download', views.download, name="download")
]