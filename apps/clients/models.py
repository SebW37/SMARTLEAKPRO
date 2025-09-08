"""
Client models for SmartLeakPro application (SQLite version).
"""
from django.db import models
from django.contrib.auth.models import User


class Client(models.Model):
    """Client model for managing customer information."""
    
    CLIENT_TYPE_CHOICES = [
        ('individual', 'Particulier'),
        ('company', 'Entreprise'),
        ('public', 'Public'),
    ]
    
    # Basic information
    name = models.CharField(max_length=200, verbose_name="Nom")
    client_type = models.CharField(max_length=20, choices=CLIENT_TYPE_CHOICES, default='individual')
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Address information
    address = models.TextField(verbose_name="Adresse")
    city = models.CharField(max_length=100, verbose_name="Ville")
    postal_code = models.CharField(max_length=10, verbose_name="Code postal")
    country = models.CharField(max_length=100, default="France", verbose_name="Pays")
    
    # Geographic information (simplified for SQLite)
    latitude = models.FloatField(blank=True, null=True, verbose_name="Latitude")
    longitude = models.FloatField(blank=True, null=True, verbose_name="Longitude")
    
    # Additional information
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_clients')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Client"
        verbose_name_plural = "Clients"
    
    def __str__(self):
        return self.name


class ClientSite(models.Model):
    """Client site model for managing multiple sites per client."""
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='sites')
    name = models.CharField(max_length=200, verbose_name="Nom du site")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    
    # Address information
    address = models.TextField(verbose_name="Adresse")
    city = models.CharField(max_length=100, verbose_name="Ville")
    postal_code = models.CharField(max_length=10, verbose_name="Code postal")
    country = models.CharField(max_length=100, default="France", verbose_name="Pays")
    
    # Geographic information (simplified for SQLite)
    latitude = models.FloatField(blank=True, null=True, verbose_name="Latitude")
    longitude = models.FloatField(blank=True, null=True, verbose_name="Longitude")
    
    # Contact information
    contact_name = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nom du contact")
    contact_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone du contact")
    contact_email = models.EmailField(blank=True, null=True, verbose_name="Email du contact")
    
    # Additional information
    access_instructions = models.TextField(blank=True, null=True, verbose_name="Instructions d'accès")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['client', 'name']
        verbose_name = "Site client"
        verbose_name_plural = "Sites clients"
    
    def __str__(self):
        return f"{self.client.name} - {self.name}"


class ClientDocument(models.Model):
    """Client document model for storing files related to clients."""
    
    DOCUMENT_TYPE_CHOICES = [
        ('contract', 'Contrat'),
        ('invoice', 'Facture'),
        ('photo', 'Photo'),
        ('other', 'Autre'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200, verbose_name="Titre")
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, default='other')
    file = models.FileField(upload_to='client_documents/', verbose_name="Fichier")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    
    # Metadata
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Document client"
        verbose_name_plural = "Documents clients"
    
    def __str__(self):
        return f"{self.client.name} - {self.title}"
