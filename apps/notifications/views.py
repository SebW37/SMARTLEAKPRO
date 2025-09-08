"""
Views for notification management.
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from .models import NotificationTemplate, Notification, NotificationPreference, NotificationLog
from .serializers import (
    NotificationTemplateSerializer, NotificationSerializer, NotificationPreferenceSerializer,
    NotificationLogSerializer, NotificationCreateSerializer, NotificationMarkReadSerializer
)
from .tasks import send_notification_task


class NotificationTemplateListCreateView(generics.ListCreateAPIView):
    """List and create notification templates."""
    
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['notification_type', 'trigger', 'is_active']
    search_fields = ['name', 'subject', 'message']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class NotificationTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a notification template."""
    
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]


class NotificationListCreateView(generics.ListCreateAPIView):
    """List and create notifications."""
    
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'notification_type', 'recipient', 'template']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'sent_at', 'read_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NotificationCreateSerializer
        return NotificationSerializer
    
    def get_queryset(self):
        """Filter notifications by user if not admin."""
        if self.request.user.role == 'admin':
            return Notification.objects.all()
        return Notification.objects.filter(recipient=self.request.user)


class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a notification."""
    
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter notifications by user if not admin."""
        if self.request.user.role == 'admin':
            return Notification.objects.all()
        return Notification.objects.filter(recipient=self.request.user)


class NotificationPreferenceListCreateView(generics.ListCreateAPIView):
    """List and create notification preferences."""
    
    queryset = NotificationPreference.objects.all()
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter preferences by user if not admin."""
        if self.request.user.role == 'admin':
            return NotificationPreference.objects.all()
        return NotificationPreference.objects.filter(user=self.request.user)


class NotificationPreferenceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete notification preferences."""
    
    queryset = NotificationPreference.objects.all()
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter preferences by user if not admin."""
        if self.request.user.role == 'admin':
            return NotificationPreference.objects.all()
        return NotificationPreference.objects.filter(user=self.request.user)


class NotificationLogListView(generics.ListAPIView):
    """List notification logs."""
    
    queryset = NotificationLog.objects.all()
    serializer_class = NotificationLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['action', 'notification']
    search_fields = ['notification__title', 'details']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notifications_read_view(request):
    """Mark notifications as read."""
    serializer = NotificationMarkReadSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        notification_ids = serializer.validated_data['notification_ids']
        notifications = Notification.objects.filter(
            id__in=notification_ids,
            recipient=request.user
        )
        
        for notification in notifications:
            notification.mark_as_read()
        
        return Response({'message': f'{len(notifications)} notifications marked as read'})
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_notification_view(request):
    """Send a notification immediately."""
    serializer = NotificationCreateSerializer(data=request.data)
    if serializer.is_valid():
        notification = serializer.save()
        
        # Send notification asynchronously
        send_notification_task.delay(notification.id)
        
        return Response(
            {'message': 'Notification queued for sending', 'notification_id': notification.id},
            status=status.HTTP_202_ACCEPTED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def notification_stats_view(request):
    """Get notification statistics."""
    user = request.user
    
    if user.role == 'admin':
        # Admin sees all notifications
        total_notifications = Notification.objects.count()
        unread_notifications = Notification.objects.filter(status='pending').count()
        sent_notifications = Notification.objects.filter(status='sent').count()
        delivered_notifications = Notification.objects.filter(status='delivered').count()
        read_notifications = Notification.objects.filter(status='read').count()
        failed_notifications = Notification.objects.filter(status='failed').count()
    else:
        # Regular users see only their notifications
        user_notifications = Notification.objects.filter(recipient=user)
        total_notifications = user_notifications.count()
        unread_notifications = user_notifications.filter(status='pending').count()
        sent_notifications = user_notifications.filter(status='sent').count()
        delivered_notifications = user_notifications.filter(status='delivered').count()
        read_notifications = user_notifications.filter(status='read').count()
        failed_notifications = user_notifications.filter(status='failed').count()
    
    stats = {
        'total_notifications': total_notifications,
        'unread_notifications': unread_notifications,
        'sent_notifications': sent_notifications,
        'delivered_notifications': delivered_notifications,
        'read_notifications': read_notifications,
        'failed_notifications': failed_notifications,
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def unread_notifications_view(request):
    """Get unread notifications for current user."""
    notifications = Notification.objects.filter(
        recipient=request.user,
        status__in=['pending', 'sent', 'delivered']
    ).order_by('-created_at')
    
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)
