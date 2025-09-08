"""
Intervention models for SmartLeakPro application.
"""
from django.db import models
# # # # from django.contrib.gis.db import models as gis_models
from django.utils import timezone
from django.contrib.auth.models import User
from apps.clients.models import Client, ClientSite


class Intervention(models.Model):
    """Intervention model for managing work orders and interventions."""
    
    STATUS_CHOICES = [
        ('scheduled', 'Planifiée'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminée'),
        ('cancelled', 'Annulée'),
        ('postponed', 'Reportée'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Faible'),
        ('medium', 'Moyenne'),
        ('high', 'Haute'),
        ('urgent', 'Urgente'),
    ]
    
    INTERVENTION_TYPE_CHOICES = [
        ('inspection', 'Inspection'),
        ('repair', 'Réparation'),
        ('maintenance', 'Maintenance'),
        ('emergency', 'Urgence'),
        ('other', 'Autre'),
    ]
    
    # Basic information
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    intervention_type = models.CharField(max_length=20, choices=INTERVENTION_TYPE_CHOICES, default='inspection')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Client and site information
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='interventions')
    site = models.ForeignKey(ClientSite, on_delete=models.CASCADE, related_name='interventions', blank=True, null=True)
    
    # Scheduling information
    scheduled_date = models.DateTimeField(verbose_name="Date planifiée")
    estimated_duration = models.DurationField(blank=True, null=True, verbose_name="Durée estimée")
    actual_start_date = models.DateTimeField(blank=True, null=True, verbose_name="Date de début réelle")
    actual_end_date = models.DateTimeField(blank=True, null=True, verbose_name="Date de fin réelle")
    
    # Assignment information
    assigned_technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                          related_name='assigned_interventions', verbose_name="Technicien assigné")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name='created_interventions', verbose_name="Créé par")
    
    # Location information
    latitude = models.FloatField(blank=True, null=True, verbose_name="Localisation")
    address = models.TextField(blank=True, null=True, verbose_name="Adresse")
    
    # Additional information
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    materials_needed = models.TextField(blank=True, null=True, verbose_name="Matériel nécessaire")
    special_instructions = models.TextField(blank=True, null=True, verbose_name="Instructions spéciales")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_date']
        verbose_name = "Intervention"
        verbose_name_plural = "Interventions"
    
    def __str__(self):
        return f"{self.title} - {self.client.name}"
    
    @property
    def is_overdue(self):
        """Check if intervention is overdue."""
        if self.status in ['completed', 'cancelled']:
            return False
        return timezone.now() > self.scheduled_date
    
    @property
    def duration(self):
        """Calculate actual duration if completed."""
        if self.actual_start_date and self.actual_end_date:
            return self.actual_end_date - self.actual_start_date
        return None


class InterventionTask(models.Model):
    """Task model for breaking down interventions into smaller tasks."""
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminée'),
        ('cancelled', 'Annulée'),
    ]
    
    intervention = models.ForeignKey(Intervention, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    
    # Assignment
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='assigned_tasks', verbose_name="Assigné à")
    
    # Timing
    estimated_duration = models.DurationField(blank=True, null=True, verbose_name="Durée estimée")
    actual_duration = models.DurationField(blank=True, null=True, verbose_name="Durée réelle")
    started_at = models.DateTimeField(blank=True, null=True, verbose_name="Débuté à")
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name="Terminé à")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['intervention', 'order']
        verbose_name = "Tâche d'intervention"
        verbose_name_plural = "Tâches d'intervention"
    
    def __str__(self):
        return f"{self.intervention.title} - {self.title}"


class InterventionDocument(models.Model):
    """Document model for intervention-related files."""
    
    DOCUMENT_TYPE_CHOICES = [
        ('photo', 'Photo'),
        ('video', 'Vidéo'),
        ('audio', 'Audio'),
        ('report', 'Rapport'),
        ('invoice', 'Facture'),
        ('other', 'Autre'),
    ]
    
    intervention = models.ForeignKey(Intervention, on_delete=models.CASCADE, related_name='documents')
    task = models.ForeignKey(InterventionTask, on_delete=models.CASCADE, related_name='documents', blank=True, null=True)
    
    title = models.CharField(max_length=200, verbose_name="Titre")
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, default='photo')
    file = models.FileField(upload_to='intervention_documents/', verbose_name="Fichier")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    
    # Location information
    latitude = models.FloatField(blank=True, null=True, verbose_name="Localisation")
    
    # Metadata
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Document d'intervention"
        verbose_name_plural = "Documents d'intervention"
    
    def __str__(self):
        return f"{self.intervention.title} - {self.title}"


class InterventionNote(models.Model):
    intervention = models.ForeignKey(Intervention, on_delete=models.CASCADE, related_name='intervention_notes')
    # ... rest of the fields    """Note model for intervention comments and updates."""
    
    task = models.ForeignKey(InterventionTask, on_delete=models.CASCADE, related_name='notes', blank=True, null=True)
    
    title = models.CharField(max_length=200, verbose_name="Titre")
    content = models.TextField(verbose_name="Contenu")
    is_internal = models.BooleanField(default=True, verbose_name="Note interne")
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Note d'intervention"
        verbose_name_plural = "Notes d'intervention"
    
    def __str__(self):
        return f"{self.intervention.title} - {self.title}"
