from django.contrib import admin
from django.urls import path
from . import views

app_name = "classifier"

urlpatterns = [
    path('', views.index, name='index'),
    path('start_classification', views.start_classification, name='start_classification'),
    #path('show_input', views.show_input, name='show_input'),
    #path('process_submit', views.process_submit, name='process_submit'),
    #path('send_client_specs', views.send_client_specs, name='send_client_specs')
]