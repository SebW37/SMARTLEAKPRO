"""
URLs for inspections app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Inspection templates
    path('templates/', views.InspectionTemplateListCreateView.as_view(), name='inspection-template-list'),
    path('templates/<int:pk>/', views.InspectionTemplateDetailView.as_view(), name='inspection-template-detail'),
    
    # Inspections
    path('', views.InspectionListCreateView.as_view(), name='inspection-list'),
    path('<int:pk>/', views.InspectionDetailView.as_view(), name='inspection-detail'),
    path('<int:pk>/start/', views.start_inspection_view, name='inspection-start'),
    path('<int:pk>/complete/', views.complete_inspection_view, name='inspection-complete'),
    path('<int:pk>/validate/', views.validate_inspection_view, name='inspection-validate'),
    path('stats/', views.inspection_stats_view, name='inspection-stats'),
    
    # Inspection items
    path('items/', views.InspectionItemListCreateView.as_view(), name='inspection-item-list'),
    path('items/<int:pk>/', views.InspectionItemDetailView.as_view(), name='inspection-item-detail'),
    
    # Inspection media
    path('media/', views.InspectionMediaListCreateView.as_view(), name='inspection-media-list'),
    path('media/<int:pk>/', views.InspectionMediaDetailView.as_view(), name='inspection-media-detail'),
    
    # Inspection signatures
    path('signatures/', views.InspectionSignatureListCreateView.as_view(), name='inspection-signature-list'),
    path('signatures/<int:pk>/', views.InspectionSignatureDetailView.as_view(), name='inspection-signature-detail'),
]
