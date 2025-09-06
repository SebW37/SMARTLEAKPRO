"""
Admin configuration for notification models.
"""
from django.contrib import admin
from .models import NotificationTemplate, Notification, NotificationPreference, NotificationLog


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    """Admin configuration for NotificationTemplate model."""
    
    list_display = [
        'name', 'notification_type', 'trigger', 'is_active', 'created_by', 'created_at'
    ]
    list_filter = ['notification_type', 'trigger', 'is_active', 'created_at']
    search_fields = ['name', 'subject', 'message']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin configuration for Notification model."""
    
    list_display = [
        'title', 'recipient', 'notification_type', 'status', 'created_at', 'sent_at'
    ]
    list_filter = ['status', 'notification_type', 'created_at', 'sent_at']
    search_fields = ['title', 'message', 'recipient__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'sent_at', 'delivered_at', 'read_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'message', 'notification_type', 'status')
        }),
        ('Destinataire', {
            'fields': ('recipient',)
        }),
        ('Template', {
            'fields': ('template',)
        }),
        ('Objet lié', {
            'fields': ('related_object_type', 'related_object_id')
        }),
        ('Livraison', {
            'fields': ('sent_at', 'delivered_at', 'read_at', 'error_message', 'retry_count')
        }),
        ('Données', {
            'fields': ('data',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """Admin configuration for NotificationPreference model."""
    
    list_display = [
        'user', 'email_enabled', 'sms_enabled', 'push_enabled', 'in_app_enabled'
    ]
    list_filter = ['email_enabled', 'sms_enabled', 'push_enabled', 'in_app_enabled']
    search_fields = ['user__username', 'user__email']
    ordering = ['user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    """Admin configuration for NotificationLog model."""
    
    list_display = [
        'notification', 'action', 'timestamp'
    ]
    list_filter = ['action', 'timestamp']
    search_fields = ['notification__title', 'details']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']
