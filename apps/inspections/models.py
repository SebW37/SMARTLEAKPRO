"""
Inspection models for SmartLeakPro application.
"""
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from django.utils import timezone
from apps.core.models import User
from apps.clients.models import Client, ClientSite
from apps.interventions.models import Intervention


class InspectionTemplate(models.Model):
    """Template for creating inspection forms."""
    
    name = models.CharField(max_length=200, verbose_name="Nom du template")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    category = models.CharField(max_length=100, verbose_name="Catégorie")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    # Template configuration
    form_config = models.JSONField(default=dict, verbose_name="Configuration du formulaire")
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Template d'inspection"
        verbose_name_plural = "Templates d'inspection"
    
    def __str__(self):
        return self.name


class Inspection(models.Model):
    """Inspection model for managing inspection data."""
    
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminée'),
        ('validated', 'Validée'),
        ('rejected', 'Rejetée'),
    ]
    
    # Basic information
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Template and form data
    template = models.ForeignKey(InspectionTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    form_data = models.JSONField(default=dict, verbose_name="Données du formulaire")
    
    # Client and site information
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='inspections')
    site = models.ForeignKey(ClientSite, on_delete=models.CASCADE, related_name='inspections', blank=True, null=True)
    
    # Intervention relationship
    intervention = models.ForeignKey(Intervention, on_delete=models.SET_NULL, null=True, blank=True, related_name='inspections')
    
    # Location information
    location = gis_models.PointField(blank=True, null=True, verbose_name="Localisation")
    address = models.TextField(blank=True, null=True, verbose_name="Adresse")
    
    # Timing information
    inspection_date = models.DateTimeField(default=timezone.now, verbose_name="Date d'inspection")
    started_at = models.DateTimeField(blank=True, null=True, verbose_name="Débuté à")
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name="Terminé à")
    
    # Assignment information
    inspector = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                 related_name='conducted_inspections', verbose_name="Inspecteur")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name='created_inspections', verbose_name="Créé par")
    
    # Results and scoring
    score = models.FloatField(blank=True, null=True, verbose_name="Score")
    max_score = models.FloatField(blank=True, null=True, verbose_name="Score maximum")
    compliance_status = models.CharField(max_length=50, blank=True, null=True, verbose_name="Statut de conformité")
    
    # Additional information
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    recommendations = models.TextField(blank=True, null=True, verbose_name="Recommandations")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-inspection_date']
        verbose_name = "Inspection"
        verbose_name_plural = "Inspections"
    
    def __str__(self):
        return f"{self.title} - {self.client.name}"
    
    @property
    def duration(self):
        """Calculate inspection duration if completed."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    @property
    def score_percentage(self):
        """Calculate score as percentage."""
        if self.score and self.max_score:
            return (self.score / self.max_score) * 100
        return None


class InspectionItem(models.Model):
    """Individual inspection item within an inspection."""
    
    ITEM_TYPE_CHOICES = [
        ('text', 'Texte'),
        ('number', 'Nombre'),
        ('boolean', 'Oui/Non'),
        ('choice', 'Choix multiple'),
        ('photo', 'Photo'),
        ('video', 'Vidéo'),
        ('audio', 'Audio'),
        ('signature', 'Signature'),
        ('location', 'Localisation'),
    ]
    
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name='items')
    template_item_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Item information
    label = models.CharField(max_length=200, verbose_name="Libellé")
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES, verbose_name="Type d'élément")
    value = models.TextField(blank=True, null=True, verbose_name="Valeur")
    
    # Configuration
    is_required = models.BooleanField(default=False, verbose_name="Requis")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    
    # Conditional logic
    show_condition = models.JSONField(default=dict, blank=True, verbose_name="Condition d'affichage")
    
    # Location information
    location = gis_models.PointField(blank=True, null=True, verbose_name="Localisation")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['inspection', 'order']
        verbose_name = "Élément d'inspection"
        verbose_name_plural = "Éléments d'inspection"
    
    def __str__(self):
        return f"{self.inspection.title} - {self.label}"


class InspectionMedia(models.Model):
    """Media files associated with inspections."""
    
    MEDIA_TYPE_CHOICES = [
        ('photo', 'Photo'),
        ('video', 'Vidéo'),
        ('audio', 'Audio'),
        ('document', 'Document'),
    ]
    
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name='media')
    item = models.ForeignKey(InspectionItem, on_delete=models.CASCADE, related_name='media', blank=True, null=True)
    
    title = models.CharField(max_length=200, verbose_name="Titre")
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES, verbose_name="Type de média")
    file = models.FileField(upload_to='inspection_media/', verbose_name="Fichier")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    
    # Location information
    location = gis_models.PointField(blank=True, null=True, verbose_name="Localisation")
    captured_at = models.DateTimeField(default=timezone.now, verbose_name="Capturé à")
    
    # Metadata
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Média d'inspection"
        verbose_name_plural = "Médias d'inspection"
    
    def __str__(self):
        return f"{self.inspection.title} - {self.title}"


class InspectionSignature(models.Model):
    """Digital signatures for inspections."""
    
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name='signatures')
    item = models.ForeignKey(InspectionItem, on_delete=models.CASCADE, related_name='signatures', blank=True, null=True)
    
    signer_name = models.CharField(max_length=200, verbose_name="Nom du signataire")
    signer_role = models.CharField(max_length=100, verbose_name="Rôle du signataire")
    signature_data = models.TextField(verbose_name="Données de signature")
    
    # Location information
    location = gis_models.PointField(blank=True, null=True, verbose_name="Localisation")
    signed_at = models.DateTimeField(default=timezone.now, verbose_name="Signé à")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-signed_at']
        verbose_name = "Signature d'inspection"
        verbose_name_plural = "Signatures d'inspection"
    
    def __str__(self):
        return f"{self.inspection.title} - {self.signer_name}"
