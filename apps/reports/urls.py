from django.urls import path
from . import views_simple

app_name = 'reports'

urlpatterns = [
    path('', views_simple.report_list, name='report_list'),
    path('create/', views_simple.report_create, name='report_create'),
    path('<uuid:pk>/', views_simple.report_detail, name='report_detail'),
    path('<uuid:pk>/edit/', views_simple.report_edit, name='report_edit'),
    path('templates/', views_simple.template_list, name='template_list'),
    path('templates/<uuid:pk>/', views_simple.template_detail, name='template_detail'),
]
