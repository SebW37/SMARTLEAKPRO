"""
Admin configuration for report models.
"""
from django.contrib import admin
from .models import ReportTemplate, Report, ReportSchedule, ReportAnalytics


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    """Admin configuration for ReportTemplate model."""
    
    list_display = ['name', 'template_type', 'is_active', 'created_by', 'created_at']
    list_filter = ['template_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Admin configuration for Report model."""
    
    list_display = [
        'title', 'status', 'format', 'client', 'intervention', 'inspection',
        'created_by', 'generated_at', 'file_size'
    ]
    list_filter = ['status', 'format', 'generated_at', 'created_at']
    search_fields = ['title', 'description', 'client__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'generation_duration', 'file_size']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'description', 'status', 'format', 'template')
        }),
        ('Objets liés', {
            'fields': ('client', 'intervention', 'inspection')
        }),
        ('Contenu', {
            'fields': ('content',)
        }),
        ('Fichier', {
            'fields': ('file', 'file_size')
        }),
        ('Génération', {
            'fields': ('generated_at', 'generation_duration')
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    """Admin configuration for ReportSchedule model."""
    
    list_display = [
        'name', 'template', 'frequency', 'is_active', 'last_run', 'next_run'
    ]
    list_filter = ['frequency', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at', 'last_run', 'next_run']


@admin.register(ReportAnalytics)
class ReportAnalyticsAdmin(admin.ModelAdmin):
    """Admin configuration for ReportAnalytics model."""
    
    list_display = [
        'report', 'view_count', 'download_count', 'last_viewed_at', 'last_downloaded_at'
    ]
    list_filter = ['created_at', 'last_viewed_at', 'last_downloaded_at']
    search_fields = ['report__title']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
