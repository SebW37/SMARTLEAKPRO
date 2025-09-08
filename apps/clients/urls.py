"""
URLs for clients app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Clients
    path('', views.ClientListCreateView.as_view(), name='client-list'),
    path('<int:pk>/', views.ClientDetailView.as_view(), name='client-detail'),
    path('stats/', views.client_stats_view, name='client-stats'),
    
    # Client sites
    path('sites/', views.ClientSiteListCreateView.as_view(), name='client-site-list'),
    path('sites/<int:pk>/', views.ClientSiteDetailView.as_view(), name='client-site-detail'),
    
    # Client documents
    path('documents/', views.ClientDocumentListCreateView.as_view(), name='client-document-list'),
    path('documents/<int:pk>/', views.ClientDocumentDetailView.as_view(), name='client-document-detail'),
    
    # Client notes
]

# Web views
from . import views_web
urlpatterns += [
    path('', views_web.client_list_view, name='client-list-web'),
]
