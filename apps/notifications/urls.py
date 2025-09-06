"""
URLs for notifications app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Notification templates
    path('templates/', views.NotificationTemplateListCreateView.as_view(), name='notification-template-list'),
    path('templates/<int:pk>/', views.NotificationTemplateDetailView.as_view(), name='notification-template-detail'),
    
    # Notifications
    path('', views.NotificationListCreateView.as_view(), name='notification-list'),
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    path('send/', views.send_notification_view, name='notification-send'),
    path('mark-read/', views.mark_notifications_read_view, name='notification-mark-read'),
    path('unread/', views.unread_notifications_view, name='notification-unread'),
    path('stats/', views.notification_stats_view, name='notification-stats'),
    
    # Notification preferences
    path('preferences/', views.NotificationPreferenceListCreateView.as_view(), name='notification-preference-list'),
    path('preferences/<int:pk>/', views.NotificationPreferenceDetailView.as_view(), name='notification-preference-detail'),
    
    # Notification logs
    path('logs/', views.NotificationLogListView.as_view(), name='notification-log-list'),
]
