from django.contrib import admin
from django.urls import path
from . import views

app_name = "classifier"

urlpatterns = [
    path('', views.hello_world),
    path('show_input', views.show_input),
]