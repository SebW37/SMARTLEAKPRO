"""
Intervention models for SmartLeakPro application.
"""
from django.db import models
from django.contrib.auth.models import User
from clients.models import Client, ClientSite


class LeakType(models.Model):
    """Types de fuites gérées par l'application."""
    
    SEVERITY_CHOICES = [
        (1, 'Faible'),
        (2, 'Moyenne'),
        (3, 'Élevée'),
        (4, 'Critique'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nom du type de fuite")
    description = models.TextField(verbose_name="Description")
    severity_level = models.IntegerField(choices=SEVERITY_CHOICES, default=2, verbose_name="Niveau de gravité")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        ordering = ['severity_level', 'name']
        verbose_name = "Type de fuite"
        verbose_name_plural = "Types de fuites"
    
    def __str__(self):
        return f"{self.name} (Niveau {self.severity_level})"


class Equipment(models.Model):
    """Équipements de détection et réparation."""
    
    CATEGORY_CHOICES = [
        ('detection', 'Détection'),
        ('measurement', 'Mesure'),
        ('documentation', 'Documentation'),
        ('repair', 'Réparation'),
        ('safety', 'Sécurité'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nom de l'équipement")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name="Catégorie")
    description = models.TextField(blank=True, verbose_name="Description")
    model = models.CharField(max_length=100, blank=True, verbose_name="Modèle")
    serial_number = models.CharField(max_length=100, blank=True, verbose_name="Numéro de série")
    available = models.BooleanField(default=True, verbose_name="Disponible")
    maintenance_due = models.DateField(blank=True, null=True, verbose_name="Maintenance due")
    location = models.CharField(max_length=100, blank=True, verbose_name="Emplacement")
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    class Meta:
        ordering = ['category', 'name']
        verbose_name = "Équipement"
        verbose_name_plural = "Équipements"
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Intervention(models.Model):
    """Modèle principal pour les interventions de recherche de fuites."""
    
    PRIORITY_CHOICES = [
        ('critical', 'Critique - Gaz, inondation'),
        ('high', 'Élevée - Eau chaude, chauffage'),
        ('medium', 'Moyenne - Eau froide'),
        ('low', 'Faible - Évacuation, maintenance'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Planifiée'),
        ('confirmed', 'Confirmée'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminée'),
        ('cancelled', 'Annulée'),
        ('postponed', 'Reportée'),
    ]
    
    # Identification
    intervention_id = models.CharField(max_length=20, unique=True, verbose_name="ID Intervention")
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    
    # Client et Site
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Client")
    site = models.ForeignKey(ClientSite, on_delete=models.CASCADE, verbose_name="Site")
    
    # Planification
    scheduled_date = models.DateTimeField(verbose_name="Date planifiée")
    estimated_duration = models.DurationField(verbose_name="Durée estimée")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name="Priorité")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', verbose_name="Statut")
    
    # Technicien assigné
    technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_interventions', verbose_name="Technicien principal")
    team_members = models.ManyToManyField(User, related_name='intervention_team', blank=True, verbose_name="Équipe")
    
    # Géolocalisation
    latitude = models.FloatField(blank=True, null=True, verbose_name="Latitude")
    longitude = models.FloatField(blank=True, null=True, verbose_name="Longitude")
    address_notes = models.TextField(blank=True, verbose_name="Notes d'adresse")
    
    # Types de fuites et équipements
    leak_types = models.ManyToManyField(LeakType, blank=True, verbose_name="Types de fuites")
    equipment_needed = models.ManyToManyField(Equipment, blank=True, verbose_name="Équipements nécessaires")
    
    # Résultats
    actual_start_time = models.DateTimeField(blank=True, null=True, verbose_name="Heure de début réelle")
    actual_end_time = models.DateTimeField(blank=True, null=True, verbose_name="Heure de fin réelle")
    findings = models.TextField(blank=True, verbose_name="Découvertes")
    recommendations = models.TextField(blank=True, verbose_name="Recommandations")
    client_notes = models.TextField(blank=True, verbose_name="Notes client")
    
    # Métadonnées
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_interventions', verbose_name="Créé par")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        ordering = ['-scheduled_date']
        verbose_name = "Intervention"
        verbose_name_plural = "Interventions"
    
    def __str__(self):
        return f"{self.intervention_id} - {self.title} ({self.client.name})"
    
    def save(self, *args, **kwargs):
        if not self.intervention_id:
            # Générer un ID unique automatiquement
            from datetime import datetime
            year = datetime.now().year
            last_intervention = Intervention.objects.filter(
                intervention_id__startswith=f"INT-{year}-"
            ).order_by('-intervention_id').first()
            
            if last_intervention:
                last_number = int(last_intervention.intervention_id.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.intervention_id = f"INT-{year}-{new_number:03d}"
        
        super().save(*args, **kwargs)


class InterventionPhoto(models.Model):
    """Photos prises pendant les interventions."""
    
    intervention = models.ForeignKey(Intervention, on_delete=models.CASCADE, related_name='photos', verbose_name="Intervention")
    photo = models.ImageField(upload_to='interventions/photos/%Y/%m/%d/', verbose_name="Photo")
    caption = models.CharField(max_length=200, blank=True, verbose_name="Légende")
    location = models.CharField(max_length=100, blank=True, verbose_name="Localisation")
    taken_at = models.DateTimeField(auto_now_add=True, verbose_name="Pris le")
    is_before = models.BooleanField(default=False, verbose_name="Photo avant intervention")
    is_after = models.BooleanField(default=False, verbose_name="Photo après intervention")
    
    class Meta:
        ordering = ['-taken_at']
        verbose_name = "Photo d'intervention"
        verbose_name_plural = "Photos d'intervention"
    
    def __str__(self):
        return f"Photo {self.intervention.intervention_id} - {self.caption or 'Sans légende'}"


class TechnicianAvailability(models.Model):
    """Disponibilités des techniciens."""
    
    technician = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availabilities', verbose_name="Technicien")
    date = models.DateField(verbose_name="Date")
    start_time = models.TimeField(verbose_name="Heure de début")
    end_time = models.TimeField(verbose_name="Heure de fin")
    is_available = models.BooleanField(default=True, verbose_name="Disponible")
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    class Meta:
        ordering = ['date', 'start_time']
        unique_together = ['technician', 'date', 'start_time']
        verbose_name = "Disponibilité technicien"
        verbose_name_plural = "Disponibilités techniciens"
    
    def __str__(self):
        status = "Disponible" if self.is_available else "Indisponible"
        return f"{self.technician.get_full_name()} - {self.date} {self.start_time}-{self.end_time} ({status})"


class InterventionReport(models.Model):
    """Rapports d'intervention générés."""
    
    REPORT_TYPE_CHOICES = [
        ('preliminary', 'Rapport préliminaire'),
        ('final', 'Rapport final'),
        ('follow_up', 'Rapport de suivi'),
    ]
    
    intervention = models.ForeignKey(Intervention, on_delete=models.CASCADE, related_name='reports', verbose_name="Intervention")
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES, default='final', verbose_name="Type de rapport")
    title = models.CharField(max_length=200, verbose_name="Titre du rapport")
    content = models.TextField(verbose_name="Contenu")
    summary = models.TextField(verbose_name="Résumé")
    recommendations = models.TextField(verbose_name="Recommandations")
    next_steps = models.TextField(blank=True, verbose_name="Prochaines étapes")
    
    # Fichiers
    pdf_file = models.FileField(upload_to='interventions/reports/%Y/%m/%d/', blank=True, null=True, verbose_name="Fichier PDF")
    
    # Métadonnées
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Créé par")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Rapport d'intervention"
        verbose_name_plural = "Rapports d'intervention"
    
    def __str__(self):
        return f"{self.intervention.intervention_id} - {self.title}"