"""
URLs for clients app.
"""
from django.urls import path
from . import views, views_web

urlpatterns = [
    # API URLs
    path('api/', views.ClientListCreateView.as_view(), name='client-list'),
    path('api/<int:pk>/', views.ClientDetailView.as_view(), name='client-detail'),
    path('api/sites/', views.ClientSiteListCreateView.as_view(), name='client-site-list'),
    path('api/sites/<int:pk>/', views.ClientSiteDetailView.as_view(), name='client-site-detail'),
    path('api/documents/', views.ClientDocumentListCreateView.as_view(), name='client-document-list'),
    path('api/documents/<int:pk>/', views.ClientDocumentDetailView.as_view(), name='client-document-detail'),
    path('api/stats/', views.client_stats_view, name='client-stats'),
    
    # Web URLs
    path('', views_web.client_list_view, name='client-list-web'),
]
