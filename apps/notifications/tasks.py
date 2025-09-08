"""
Celery tasks for notifications.
"""
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification, NotificationLog

# Optional Celery import
try:
    from celery import shared_task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    # Fallback decorator that does nothing
    def shared_task(func):
        return func


@shared_task
def send_notification_task(notification_id):
    """Send a notification asynchronously."""
    try:
        notification = Notification.objects.get(id=notification_id)
        
        # Log sending attempt
        NotificationLog.objects.create(
            notification=notification,
            action='sent',
            details='Starting notification send process'
        )
        
        # Send based on notification type
        if notification.notification_type == 'email':
            success = send_email_notification(notification)
        elif notification.notification_type == 'sms':
            success = send_sms_notification(notification)
        elif notification.notification_type == 'push':
            success = send_push_notification(notification)
        elif notification.notification_type == 'in_app':
            success = send_in_app_notification(notification)
        else:
            success = False
        
        if success:
            notification.mark_as_sent()
            NotificationLog.objects.create(
                notification=notification,
                action='sent',
                details='Notification sent successfully'
            )
        else:
            notification.mark_as_failed("Failed to send notification")
            NotificationLog.objects.create(
                notification=notification,
                action='failed',
                details='Failed to send notification'
            )
        
        return f"Notification {notification_id} processed"
        
    except Notification.DoesNotExist:
        return f"Notification {notification_id} not found"
    except Exception as e:
        # Log error
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.mark_as_failed(str(e))
            NotificationLog.objects.create(
                notification=notification,
                action='failed',
                details=f"Error: {str(e)}"
            )
        except:
            pass
        
        raise e


def send_email_notification(notification):
    """Send email notification."""
    try:
        send_mail(
            subject=notification.title,
            message=notification.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.recipient.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email send error: {e}")
        return False


def send_sms_notification(notification):
    """Send SMS notification."""
    # This would integrate with an SMS service like Twilio
    # For now, just log the attempt
    print(f"SMS to {notification.recipient.phone}: {notification.message}")
    return True


def send_push_notification(notification):
    """Send push notification."""
    # This would integrate with a push notification service
    # For now, just log the attempt
    print(f"Push to {notification.recipient.username}: {notification.title}")
    return True


def send_in_app_notification(notification):
    """Send in-app notification."""
    # In-app notifications are stored in the database
    # No additional sending required
    return True
