"""
URL configuration for clients app.
"""
from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    path('', views.client_list, name='client_list'),
    path('<int:client_id>/', views.client_detail, name='client_detail'),
]
