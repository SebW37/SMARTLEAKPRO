"""
URLs for core app.
"""
from django.urls import path, include
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.profile_update_view, name='profile-update'),
    
    # Users
    path('users/', views.UserListCreateView.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    
    # Companies
    path('companies/', views.CompanyListCreateView.as_view(), name='company-list'),
    path('companies/<int:pk>/', views.CompanyDetailView.as_view(), name='company-detail'),
    
    # Audit logs
    path('audit-logs/', views.AuditLogListView.as_view(), name='audit-log-list'),
    
    # Geolocation
    path('geolocation/', include('apps.core.urls.geolocation')),
    
    # Offline synchronization
    path('offline/', include('apps.core.urls.offline_sync')),
]
