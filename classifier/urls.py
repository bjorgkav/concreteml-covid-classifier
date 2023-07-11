from django.contrib import admin
from django.urls import path
from . import views

app_name = "classifier"

urlpatterns = [
    path('', views.index, name='index'),
    path('start_classification', views.start_classification, name='start_classification'),
    path('download', views.serve_downloadable, name='download'),
]