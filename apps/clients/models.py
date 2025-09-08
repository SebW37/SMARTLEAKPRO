"""
Client models for SmartLeakPro application (SQLite version).
Enhanced according to functional specifications.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
import uuid


class Client(models.Model):
    """Client model for managing customer information."""
    
    CLIENT_TYPE_CHOICES = [
        ('individual', 'Particulier'),
        ('company', 'Entreprise'),
        ('public', 'Collectivité'),
        ('syndic', 'Syndic'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('inactive', 'Inactif/Suspendu'),
        ('prospect', 'Prospect'),
        ('archived', 'Archivé'),
    ]
    
    CONTRACT_TYPE_CHOICES = [
        ('maintenance', 'Maintenance'),
        ('detection', 'Détection de fuites'),
        ('emergency', 'Urgence'),
        ('consulting', 'Conseil'),
        ('other', 'Autre'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('bank_transfer', 'Virement bancaire'),
        ('check', 'Chèque'),
        ('card', 'Carte bancaire'),
        ('cash', 'Espèces'),
        ('other', 'Autre'),
    ]
    
    # Unique client number (auto-generated)
    client_number = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name="Numéro client",
        help_text="Numéro unique généré automatiquement"
    )
    
    # Basic information
    name = models.CharField(max_length=200, verbose_name="Raison sociale / Nom")
    client_type = models.CharField(max_length=20, choices=CLIENT_TYPE_CHOICES, default='individual', verbose_name="Type")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Statut")
    
    # Contact information
    email = models.EmailField(blank=True, null=True, verbose_name="Email principal")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone principal")
    secondary_email = models.EmailField(blank=True, null=True, verbose_name="Email secondaire")
    secondary_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone secondaire")
    
    # Address information
    address = models.TextField(verbose_name="Adresse principale")
    city = models.CharField(max_length=100, verbose_name="Ville")
    postal_code = models.CharField(max_length=10, verbose_name="Code postal")
    country = models.CharField(max_length=100, default="France", verbose_name="Pays")
    
    # Geographic information (simplified for SQLite)
    latitude = models.FloatField(blank=True, null=True, verbose_name="Latitude")
    longitude = models.FloatField(blank=True, null=True, verbose_name="Longitude")
    
    # Contract information
    contract_type = models.CharField(
        max_length=20, 
        choices=CONTRACT_TYPE_CHOICES, 
        blank=True, 
        null=True, 
        verbose_name="Type de contrat"
    )
    contract_start_date = models.DateField(blank=True, null=True, verbose_name="Date début contrat")
    contract_end_date = models.DateField(blank=True, null=True, verbose_name="Date fin contrat")
    
    # Billing information
    billing_address = models.TextField(blank=True, null=True, verbose_name="Adresse de facturation")
    billing_city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ville facturation")
    billing_postal_code = models.CharField(max_length=10, blank=True, null=True, verbose_name="CP facturation")
    siret = models.CharField(
        max_length=14, 
        blank=True, 
        null=True, 
        verbose_name="SIRET",
        validators=[RegexValidator(regex=r'^\d{14}$', message='SIRET doit contenir 14 chiffres')]
    )
    siren = models.CharField(
        max_length=9, 
        blank=True, 
        null=True, 
        verbose_name="SIREN",
        validators=[RegexValidator(regex=r'^\d{9}$', message='SIREN doit contenir 9 chiffres')]
    )
    vat_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Numéro TVA")
    preferred_payment_method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHOD_CHOICES, 
        blank=True, 
        null=True, 
        verbose_name="Mode de règlement préféré"
    )
    bank_details = models.TextField(blank=True, null=True, verbose_name="Coordonnées bancaires")
    
    # Visit preferences and constraints
    visit_preferences = models.TextField(blank=True, null=True, verbose_name="Préférences de visite")
    access_constraints = models.TextField(blank=True, null=True, verbose_name="Contraintes d'accès")
    preferred_visit_days = models.CharField(max_length=100, blank=True, null=True, verbose_name="Jours préférés")
    preferred_visit_hours = models.CharField(max_length=100, blank=True, null=True, verbose_name="Heures préférées")
    
    # Additional information
    notes = models.TextField(blank=True, null=True, verbose_name="Notes libres")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    # GDPR compliance
    gdpr_consent = models.BooleanField(default=False, verbose_name="Consentement RGPD")
    gdpr_consent_date = models.DateTimeField(blank=True, null=True, verbose_name="Date consentement RGPD")
    data_retention_until = models.DateField(blank=True, null=True, verbose_name="Conservation données jusqu'au")
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_clients')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        indexes = [
            models.Index(fields=['client_number']),
            models.Index(fields=['name']),
            models.Index(fields=['status']),
            models.Index(fields=['client_type']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.client_number:
            # Generate unique client number
            self.client_number = f"CLI-{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.client_number})"


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


class ClientContact(models.Model):
    """Client contact model for managing multiple contacts per client."""
    
    ROLE_CHOICES = [
        ('primary', 'Contact principal'),
        ('technical', 'Contact technique'),
        ('billing', 'Contact facturation'),
        ('emergency', 'Contact urgence'),
        ('other', 'Autre'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='contacts')
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='other', verbose_name="Rôle")
    position = models.CharField(max_length=100, blank=True, null=True, verbose_name="Poste")
    
    # Contact information
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone")
    mobile = models.CharField(max_length=20, blank=True, null=True, verbose_name="Mobile")
    
    # Additional information
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    is_primary = models.BooleanField(default=False, verbose_name="Contact principal")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['client', 'is_primary', 'last_name', 'first_name']
        verbose_name = "Contact client"
        verbose_name_plural = "Contacts clients"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_role_display()})"


class ClientContract(models.Model):
    """Client contract model for managing contracts."""
    
    CONTRACT_STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('active', 'Actif'),
        ('suspended', 'Suspendu'),
        ('expired', 'Expiré'),
        ('terminated', 'Résilié'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='contracts')
    contract_number = models.CharField(max_length=50, unique=True, verbose_name="Numéro de contrat")
    contract_type = models.CharField(max_length=20, choices=Client.CONTRACT_TYPE_CHOICES, verbose_name="Type de contrat")
    status = models.CharField(max_length=20, choices=CONTRACT_STATUS_CHOICES, default='draft', verbose_name="Statut")
    
    # Contract dates
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(blank=True, null=True, verbose_name="Date de fin")
    renewal_date = models.DateField(blank=True, null=True, verbose_name="Date de renouvellement")
    
    # Financial information
    monthly_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Montant mensuel")
    annual_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Montant annuel")
    currency = models.CharField(max_length=3, default='EUR', verbose_name="Devise")
    
    # Contract details
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    terms_conditions = models.TextField(blank=True, null=True, verbose_name="Conditions générales")
    special_conditions = models.TextField(blank=True, null=True, verbose_name="Conditions particulières")
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_contracts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = "Contrat client"
        verbose_name_plural = "Contrats clients"
    
    def __str__(self):
        return f"{self.contract_number} - {self.client.name}"


class ClientDocument(models.Model):
    """Client document model for storing files related to clients."""
    
    DOCUMENT_TYPE_CHOICES = [
        ('contract', 'Contrat'),
        ('invoice', 'Facture'),
        ('plan', 'Plan'),
        ('photo', 'Photo'),
        ('report', 'Rapport'),
        ('certificate', 'Certificat'),
        ('other', 'Autre'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, verbose_name="Type de document")
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    
    # File information
    file_path = models.CharField(max_length=500, verbose_name="Chemin du fichier")
    file_size = models.PositiveIntegerField(blank=True, null=True, verbose_name="Taille du fichier (bytes)")
    file_type = models.CharField(max_length=50, blank=True, null=True, verbose_name="Type de fichier")
    
    # Metadata
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_documents')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False, verbose_name="Public")
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Document client"
        verbose_name_plural = "Documents clients"
    
    def __str__(self):
        return f"{self.title} - {self.client.name}"


class ClientNotification(models.Model):
    """Client notification model for tracking communications."""
    
    NOTIFICATION_TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('phone', 'Appel téléphonique'),
        ('letter', 'Courrier'),
        ('meeting', 'Rendez-vous'),
        ('other', 'Autre'),
    ]
    
    STATUS_CHOICES = [
        ('sent', 'Envoyé'),
        ('delivered', 'Livré'),
        ('read', 'Lu'),
        ('failed', 'Échec'),
        ('pending', 'En attente'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES, verbose_name="Type de notification")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    
    # Content
    subject = models.CharField(max_length=200, blank=True, null=True, verbose_name="Sujet")
    content = models.TextField(verbose_name="Contenu")
    
    # Delivery information
    sent_to = models.CharField(max_length=200, verbose_name="Envoyé à")
    sent_at = models.DateTimeField(blank=True, null=True, verbose_name="Envoyé le")
    delivered_at = models.DateTimeField(blank=True, null=True, verbose_name="Livré le")
    read_at = models.DateTimeField(blank=True, null=True, verbose_name="Lu le")
    
    # Metadata
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notification client"
        verbose_name_plural = "Notifications clients"
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.client.name}"


class ClientActivityLog(models.Model):
    """Client activity log for tracking all changes and activities."""
    
    ACTION_CHOICES = [
        ('created', 'Créé'),
        ('updated', 'Modifié'),
        ('deleted', 'Supprimé'),
        ('viewed', 'Consulté'),
        ('contacted', 'Contacté'),
        ('visited', 'Visité'),
        ('other', 'Autre'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="Action")
    description = models.TextField(verbose_name="Description")
    
    # Change tracking
    old_values = models.JSONField(blank=True, null=True, verbose_name="Anciennes valeurs")
    new_values = models.JSONField(blank=True, null=True, verbose_name="Nouvelles valeurs")
    
    # Metadata
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='client_activities')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="Adresse IP")
    user_agent = models.TextField(blank=True, null=True, verbose_name="User Agent")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Journal d'activité client"
        verbose_name_plural = "Journaux d'activité clients"
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.client.name} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"