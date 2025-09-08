"""
URLs for clients app.
"""
from django.urls import path
from . import views, views_web, views_enhanced

urlpatterns = [
    # API URLs
    path('api/', views.ClientListCreateView.as_view(), name='client-list'),
    path('api/<int:pk>/', views.ClientDetailView.as_view(), name='client-detail'),
    path('api/sites/', views.ClientSiteListCreateView.as_view(), name='client-site-list'),
    path('api/sites/<int:pk>/', views.ClientSiteDetailView.as_view(), name='client-site-detail'),
    path('api/documents/', views.ClientDocumentListCreateView.as_view(), name='client-document-list'),
    path('api/documents/<int:pk>/', views.ClientDocumentDetailView.as_view(), name='client-document-detail'),
    path('api/stats/', views.client_stats_view, name='client-stats'),
    
    # Enhanced web URLs
    path('', views_enhanced.client_list_view, name='client-list-web'),
    path('create/', views_enhanced.client_create_view, name='client-create'),
    path('<int:client_id>/', views_enhanced.client_detail_view, name='client-detail'),
    path('<int:client_id>/edit/', views_enhanced.client_edit_view, name='client-edit'),
    path('<int:client_id>/delete/', views_enhanced.client_delete_view, name='client-delete'),
    path('export/', views_enhanced.client_export_view, name='client-export'),
    path('stats/', views_enhanced.client_stats_view, name='client-stats-web'),
    path('ajax/', views_enhanced.client_ajax_view, name='client-ajax'),
    
    # Contact management
    path('<int:client_id>/contacts/create/', views_enhanced.client_contact_create_view, name='client-contact-create'),
    
    # Contract management
    path('<int:client_id>/contracts/create/', views_enhanced.client_contract_create_view, name='client-contract-create'),
]
