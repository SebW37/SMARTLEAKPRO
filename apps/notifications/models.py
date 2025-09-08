"""
Notification models for SmartLeakPro application.
"""
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class NotificationTemplate(models.Model):
    """Template for notifications."""
    
    NOTIFICATION_TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push'),
        ('in_app', 'In-App'),
    ]
    
    TRIGGER_CHOICES = [
        ('intervention_scheduled', 'Intervention planifiée'),
        ('intervention_started', 'Intervention démarrée'),
        ('intervention_completed', 'Intervention terminée'),
        ('inspection_scheduled', 'Inspection planifiée'),
        ('inspection_completed', 'Inspection terminée'),
        ('report_generated', 'Rapport généré'),
        ('overdue_intervention', 'Intervention en retard'),
        ('custom', 'Personnalisé'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nom du template")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES, verbose_name="Type de notification")
    trigger = models.CharField(max_length=50, choices=TRIGGER_CHOICES, verbose_name="Déclencheur")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    # Template content
    subject = models.CharField(max_length=200, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    html_template = models.TextField(blank=True, null=True, verbose_name="Template HTML")
    
    # Configuration
    config = models.JSONField(default=dict, verbose_name="Configuration")
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Template de notification"
        verbose_name_plural = "Templates de notification"
    
    def __str__(self):
        return self.name


class Notification(models.Model):
    """Notification model."""
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('sent', 'Envoyée'),
        ('delivered', 'Livrée'),
        ('failed', 'Échec'),
        ('read', 'Lue'),
    ]
    
    # Basic information
    title = models.CharField(max_length=200, verbose_name="Titre")
    message = models.TextField(verbose_name="Message")
    notification_type = models.CharField(max_length=20, choices=NotificationTemplate.NOTIFICATION_TYPE_CHOICES, verbose_name="Type")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    
    # Recipients
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name="Destinataire")
    
    # Template reference
    template = models.ForeignKey(NotificationTemplate, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Template")
    
    # Related objects
    related_object_type = models.CharField(max_length=50, blank=True, null=True, verbose_name="Type d'objet lié")
    related_object_id = models.PositiveIntegerField(blank=True, null=True, verbose_name="ID de l'objet lié")
    
    # Delivery information
    sent_at = models.DateTimeField(blank=True, null=True, verbose_name="Envoyé à")
    delivered_at = models.DateTimeField(blank=True, null=True, verbose_name="Livré à")
    read_at = models.DateTimeField(blank=True, null=True, verbose_name="Lu à")
    
    # Error information
    error_message = models.TextField(blank=True, null=True, verbose_name="Message d'erreur")
    retry_count = models.PositiveIntegerField(default=0, verbose_name="Nombre de tentatives")
    
    # Additional data
    data = models.JSONField(default=dict, verbose_name="Données supplémentaires")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
    
    def mark_as_sent(self):
        """Mark notification as sent."""
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save()
    
    def mark_as_delivered(self):
        """Mark notification as delivered."""
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        self.save()
    
    def mark_as_read(self):
        """Mark notification as read."""
        self.status = 'read'
        self.read_at = timezone.now()
        self.save()
    
    def mark_as_failed(self, error_message):
        """Mark notification as failed."""
        self.status = 'failed'
        self.error_message = error_message
        self.retry_count += 1
        self.save()


class NotificationPreference(models.Model):
    """User notification preferences."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email preferences
    email_enabled = models.BooleanField(default=True, verbose_name="Email activé")
    email_interventions = models.BooleanField(default=True, verbose_name="Email pour interventions")
    email_inspections = models.BooleanField(default=True, verbose_name="Email pour inspections")
    email_reports = models.BooleanField(default=True, verbose_name="Email pour rapports")
    email_reminders = models.BooleanField(default=True, verbose_name="Email pour rappels")
    
    # SMS preferences
    sms_enabled = models.BooleanField(default=False, verbose_name="SMS activé")
    sms_interventions = models.BooleanField(default=False, verbose_name="SMS pour interventions")
    sms_urgent = models.BooleanField(default=True, verbose_name="SMS pour urgences")
    
    # Push preferences
    push_enabled = models.BooleanField(default=True, verbose_name="Push activé")
    push_interventions = models.BooleanField(default=True, verbose_name="Push pour interventions")
    push_inspections = models.BooleanField(default=True, verbose_name="Push pour inspections")
    push_reports = models.BooleanField(default=False, verbose_name="Push pour rapports")
    
    # In-app preferences
    in_app_enabled = models.BooleanField(default=True, verbose_name="In-app activé")
    
    # Timing preferences
    quiet_hours_start = models.TimeField(blank=True, null=True, verbose_name="Début des heures silencieuses")
    quiet_hours_end = models.TimeField(blank=True, null=True, verbose_name="Fin des heures silencieuses")
    timezone = models.CharField(max_length=50, default='Europe/Paris', verbose_name="Fuseau horaire")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Préférence de notification"
        verbose_name_plural = "Préférences de notification"
    
    def __str__(self):
        return f"Préférences de {self.user.username}"


class NotificationLog(models.Model):
    """Log of notification activities."""
    
    ACTION_CHOICES = [
        ('sent', 'Envoyée'),
        ('delivered', 'Livrée'),
        ('read', 'Lue'),
        ('failed', 'Échec'),
        ('retry', 'Nouvelle tentative'),
    ]
    
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="Action")
    details = models.TextField(blank=True, null=True, verbose_name="Détails")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Horodatage")
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Log de notification"
        verbose_name_plural = "Logs de notification"
    
    def __str__(self):
        return f"{self.notification.title} - {self.get_action_display()}"
