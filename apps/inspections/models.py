"""
Inspection models for SmartLeakPro application (SQLite version).
"""
from django.db import models
from django.contrib.auth.models import User
from apps.clients.models import Client, ClientSite


class InspectionTemplate(models.Model):
    """Template for inspections."""
    
    name = models.CharField(max_length=200, verbose_name="Nom du modèle")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Modèle d'inspection"
        verbose_name_plural = "Modèles d'inspection"
    
    def __str__(self):
        return self.name


class Inspection(models.Model):
    """Inspection model."""
    
    STATUS_CHOICES = [
        ('scheduled', 'Planifiée'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminée'),
        ('cancelled', 'Annulée'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='inspections')
    site = models.ForeignKey(ClientSite, on_delete=models.CASCADE, related_name='inspections', null=True, blank=True)
    template = models.ForeignKey(InspectionTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    scheduled_date = models.DateTimeField(verbose_name="Date prévue")
    completed_date = models.DateTimeField(null=True, blank=True, verbose_name="Date de fin")
    
    inspector = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='inspections')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_date']
        verbose_name = "Inspection"
        verbose_name_plural = "Inspections"
    
    def __str__(self):
        return f"{self.client.name} - {self.title}"


class InspectionItem(models.Model):
    """Inspection item model."""
    
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200, verbose_name="Nom")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    is_checked = models.BooleanField(default=False, verbose_name="Vérifié")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Élément d'inspection"
        verbose_name_plural = "Éléments d'inspection"
    
    def __str__(self):
        return f"{self.inspection.title} - {self.name}"


class InspectionMedia(models.Model):
    """Inspection media model."""
    
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='inspection_media/', verbose_name="Fichier")
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Média d'inspection"
        verbose_name_plural = "Médias d'inspection"
    
    def __str__(self):
        return f"{self.inspection.title} - {self.title}"


class InspectionSignature(models.Model):
    """Inspection signature model."""
    
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name='signatures')
    signer_name = models.CharField(max_length=200, verbose_name="Nom du signataire")
    signature_image = models.ImageField(upload_to='inspection_signatures/', verbose_name="Image de signature")
    signed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-signed_at']
        verbose_name = "Signature d'inspection"
        verbose_name_plural = "Signatures d'inspection"
    
    def __str__(self):
        return f"{self.inspection.title} - {self.signer_name}"
