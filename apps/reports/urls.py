"""
URLs for reports app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Report templates
    path('templates/', views.ReportTemplateListCreateView.as_view(), name='report-template-list'),
    path('templates/<int:pk>/', views.ReportTemplateDetailView.as_view(), name='report-template-detail'),
    
    # Reports
    path('', views.ReportListCreateView.as_view(), name='report-list'),
    path('<int:pk>/', views.ReportDetailView.as_view(), name='report-detail'),
    path('generate/', views.generate_report_view, name='report-generate'),
    path('<int:pk>/download/', views.download_report_view, name='report-download'),
    path('<int:pk>/view/', views.view_report_view, name='report-view'),
    path('stats/', views.report_stats_view, name='report-stats'),
    
    # Report schedules
    path('schedules/', views.ReportScheduleListCreateView.as_view(), name='report-schedule-list'),
    path('schedules/<int:pk>/', views.ReportScheduleDetailView.as_view(), name='report-schedule-detail'),
    
    # Report analytics
    path('analytics/', views.ReportAnalyticsListView.as_view(), name='report-analytics-list'),
]
