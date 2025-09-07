from django.urls import path
from . import views_simple

app_name = 'reports'

urlpatterns = [
    # Test view
    path('', views_simple.test_view, name='test'),
    
    # Reports
    path('list/', views_simple.report_list, name='report_list'),
    path('create/', views_simple.report_create, name='report_create'),
    path('<int:report_id>/', views_simple.report_detail, name='report_detail'),
    path('<int:report_id>/edit/', views_simple.report_edit, name='report_edit'),
    
    # Templates
    path('templates/', views_simple.template_list, name='template_list'),
    path('templates/<int:template_id>/', views_simple.template_detail, name='template_detail'),
]
