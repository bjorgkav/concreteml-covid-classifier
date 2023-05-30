from django.contrib import admin
from django.urls import path
from . import views

app_name = "client"

urlpatterns = [
    path('', views.index, name='index'),
    path('show_input', views.show_input, name='show_input'),
    path('process_dashing', views.process_dashing, name='process_dashing'),
    path('process_encrypt', views.process_encrypt, name='process_encrypt'),
    path('send_client_specs', views.send_client_specs, name='send_client_specs'),
    path('download_zip', views.download_zip, name="download_zip"),
    path('show_decrypt_page', views.show_decrypt_page, name='show_decrypt_page'),
    path('process_decrypt', views.process_decrypt, name='process_decrypt'),
]