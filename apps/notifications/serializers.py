"""
Serializers for notification models.
"""
from rest_framework import serializers
from .models import NotificationTemplate, Notification, NotificationPreference, NotificationLog


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for NotificationTemplate model."""
    
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'notification_type', 'trigger', 'is_active',
            'subject', 'message', 'html_template', 'config', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model."""
    
    recipient_name = serializers.CharField(source='recipient.full_name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type', 'status',
            'recipient', 'recipient_name', 'template', 'template_name',
            'related_object_type', 'related_object_id', 'sent_at',
            'delivered_at', 'read_at', 'error_message', 'retry_count',
            'data', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for NotificationPreference model."""
    
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'user', 'user_name', 'email_enabled', 'email_interventions',
            'email_inspections', 'email_reports', 'email_reminders', 'sms_enabled',
            'sms_interventions', 'sms_urgent', 'push_enabled', 'push_interventions',
            'push_inspections', 'push_reports', 'in_app_enabled', 'quiet_hours_start',
            'quiet_hours_end', 'timezone', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationLogSerializer(serializers.ModelSerializer):
    """Serializer for NotificationLog model."""
    
    notification_title = serializers.CharField(source='notification.title', read_only=True)
    
    class Meta:
        model = NotificationLog
        fields = [
            'id', 'notification', 'notification_title', 'action', 'details',
            'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications."""
    
    class Meta:
        model = Notification
        fields = [
            'title', 'message', 'notification_type', 'recipient',
            'template', 'related_object_type', 'related_object_id', 'data'
        ]
    
    def create(self, validated_data):
        # Set default status
        validated_data['status'] = 'pending'
        return super().create(validated_data)


class NotificationMarkReadSerializer(serializers.Serializer):
    """Serializer for marking notifications as read."""
    
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )
    
    def validate_notification_ids(self, value):
        """Validate that all notification IDs exist and belong to the user."""
        user = self.context['request'].user
        notifications = Notification.objects.filter(
            id__in=value,
            recipient=user
        )
        if len(notifications) != len(value):
            raise serializers.ValidationError("Some notifications not found or not accessible.")
        return value
