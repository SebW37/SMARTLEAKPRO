"""
Report models for SmartLeakPro application.
"""
from django.db import models
from django.utils import timezone
from apps.core.models import User
from apps.clients.models import Client
from apps.interventions.models import Intervention
from apps.inspections.models import Inspection


class ReportTemplate(models.Model):
    """Template for generating reports."""
    
    TEMPLATE_TYPE_CHOICES = [
        ('inspection', 'Rapport d\'inspection'),
        ('intervention', 'Rapport d\'intervention'),
        ('summary', 'Rapport de synthèse'),
        ('custom', 'Rapport personnalisé'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nom du template")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPE_CHOICES, verbose_name="Type de template")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    # Template configuration
    template_config = models.JSONField(default=dict, verbose_name="Configuration du template")
    html_template = models.TextField(blank=True, null=True, verbose_name="Template HTML")
    css_styles = models.TextField(blank=True, null=True, verbose_name="Styles CSS")
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Template de rapport"
        verbose_name_plural = "Templates de rapport"
    
    def __str__(self):
        return self.name


class Report(models.Model):
    """Generated report model."""
    
    STATUS_CHOICES = [
        ('generating', 'En cours de génération'),
        ('completed', 'Terminé'),
        ('failed', 'Échec'),
        ('archived', 'Archivé'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('docx', 'Word'),
        ('html', 'HTML'),
        ('xlsx', 'Excel'),
    ]
    
    # Basic information
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='generating')
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='pdf')
    
    # Template and content
    template = models.ForeignKey(ReportTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.JSONField(default=dict, verbose_name="Contenu du rapport")
    
    # Related objects
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='reports', blank=True, null=True)
    intervention = models.ForeignKey(Intervention, on_delete=models.CASCADE, related_name='reports', blank=True, null=True)
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name='reports', blank=True, null=True)
    
    # File information
    file = models.FileField(upload_to='reports/', blank=True, null=True, verbose_name="Fichier")
    file_size = models.PositiveIntegerField(blank=True, null=True, verbose_name="Taille du fichier")
    
    # Generation information
    generated_at = models.DateTimeField(blank=True, null=True, verbose_name="Généré à")
    generation_duration = models.DurationField(blank=True, null=True, verbose_name="Durée de génération")
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Rapport"
        verbose_name_plural = "Rapports"
    
    def __str__(self):
        return self.title
    
    @property
    def file_url(self):
        """Get file URL if file exists."""
        if self.file:
            return self.file.url
        return None


class ReportSchedule(models.Model):
    """Scheduled report generation."""
    
    FREQUENCY_CHOICES = [
        ('daily', 'Quotidien'),
        ('weekly', 'Hebdomadaire'),
        ('monthly', 'Mensuel'),
        ('quarterly', 'Trimestriel'),
        ('yearly', 'Annuel'),
    ]
    
    # Basic information
    name = models.CharField(max_length=200, verbose_name="Nom")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    # Schedule configuration
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, verbose_name="Fréquence")
    schedule_config = models.JSONField(default=dict, verbose_name="Configuration de planification")
    
    # Recipients
    email_recipients = models.JSONField(default=list, verbose_name="Destinataires email")
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_run = models.DateTimeField(blank=True, null=True, verbose_name="Dernière exécution")
    next_run = models.DateTimeField(blank=True, null=True, verbose_name="Prochaine exécution")
    
    class Meta:
        ordering = ['name']
        verbose_name = "Planification de rapport"
        verbose_name_plural = "Planifications de rapport"
    
    def __str__(self):
        return self.name


class ReportAnalytics(models.Model):
    """Analytics data for reports."""
    
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='analytics')
    
    # View statistics
    view_count = models.PositiveIntegerField(default=0, verbose_name="Nombre de vues")
    download_count = models.PositiveIntegerField(default=0, verbose_name="Nombre de téléchargements")
    
    # User tracking
    viewed_by = models.ManyToManyField(User, blank=True, related_name='viewed_reports')
    downloaded_by = models.ManyToManyField(User, blank=True, related_name='downloaded_reports')
    
    # Timestamps
    first_viewed_at = models.DateTimeField(blank=True, null=True, verbose_name="Première vue")
    last_viewed_at = models.DateTimeField(blank=True, null=True, verbose_name="Dernière vue")
    first_downloaded_at = models.DateTimeField(blank=True, null=True, verbose_name="Premier téléchargement")
    last_downloaded_at = models.DateTimeField(blank=True, null=True, verbose_name="Dernier téléchargement")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Analytique de rapport"
        verbose_name_plural = "Analytiques de rapport"
    
    def __str__(self):
        return f"Analytics for {self.report.title}"
