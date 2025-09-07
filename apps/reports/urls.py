from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, views_django

router = DefaultRouter()
router.register(r'templates', views.ReportTemplateViewSet, basename='report-template')
router.register(r'reports', views.InterventionReportViewSet, basename='intervention-report')
router.register(r'section-data', views.ReportSectionDataViewSet, basename='report-section-data')
router.register(r'media', views.ReportMediaViewSet, basename='report-media')
router.register(r'signatures', views.ReportSignatureViewSet, basename='report-signature')
router.register(r'exports', views.ReportExportViewSet, basename='report-export')
router.register(r'history', views.ReportHistoryViewSet, basename='report-history')

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Django views
    path('', views_django.report_list, name='report_list'),
    path('create/', views_django.report_create, name='report_create'),
    path('<uuid:report_id>/', views_django.report_detail, name='report_detail'),
    path('<uuid:report_id>/edit/', views_django.report_edit, name='report_edit'),
    path('<uuid:report_id>/preview/', views_django.report_preview, name='report_preview'),
    path('templates/', views_django.template_list, name='template_list'),
    path('templates/<uuid:template_id>/', views_django.template_detail, name='template_detail'),
]