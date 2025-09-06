"""
Admin configuration for interventions app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    LeakType, Equipment, Intervention, InterventionPhoto, 
    TechnicianAvailability, InterventionReport
)


@admin.register(LeakType)
class LeakTypeAdmin(admin.ModelAdmin):
    """Admin configuration for LeakType model."""
    
    list_display = ['name', 'severity_level', 'is_active']
    list_filter = ['severity_level', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['is_active']


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    """Admin configuration for Equipment model."""
    
    list_display = ['name', 'category', 'model', 'available', 'maintenance_due', 'location']
    list_filter = ['category', 'available', 'maintenance_due']
    search_fields = ['name', 'model', 'serial_number', 'description']
    list_editable = ['available']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'category', 'model', 'serial_number', 'description')
        }),
        ('État', {
            'fields': ('available', 'maintenance_due', 'location')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )


class InterventionPhotoInline(admin.TabularInline):
    """Inline admin for InterventionPhoto."""
    model = InterventionPhoto
    extra = 0
    fields = ['photo', 'caption', 'location', 'is_before', 'is_after']


class InterventionReportInline(admin.TabularInline):
    """Inline admin for InterventionReport."""
    model = InterventionReport
    extra = 0
    fields = ['report_type', 'title', 'summary']


@admin.register(Intervention)
class InterventionAdmin(admin.ModelAdmin):
    """Admin configuration for Intervention model."""
    
    list_display = [
        'intervention_id', 'title', 'client', 'site', 'scheduled_date', 
        'technician', 'priority', 'status', 'created_at'
    ]
    list_filter = [
        'priority', 'status', 'leak_types', 'scheduled_date', 
        'technician', 'created_at'
    ]
    search_fields = [
        'intervention_id', 'title', 'client__name', 'site__name', 
        'technician__username', 'description'
    ]
    list_editable = ['status', 'priority']
    readonly_fields = ['intervention_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Identification', {
            'fields': ('intervention_id', 'title', 'description')
        }),
        ('Client et Site', {
            'fields': ('client', 'site')
        }),
        ('Planification', {
            'fields': ('scheduled_date', 'estimated_duration', 'priority', 'status')
        }),
        ('Équipe', {
            'fields': ('technician', 'team_members')
        }),
        ('Géolocalisation', {
            'fields': ('latitude', 'longitude', 'address_notes'),
            'classes': ('collapse',)
        }),
        ('Types de fuites et Équipements', {
            'fields': ('leak_types', 'equipment_needed'),
            'classes': ('collapse',)
        }),
        ('Résultats', {
            'fields': ('actual_start_time', 'actual_end_time', 'findings', 'recommendations', 'client_notes'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [InterventionPhotoInline, InterventionReportInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('client', 'site', 'technician')


@admin.register(InterventionPhoto)
class InterventionPhotoAdmin(admin.ModelAdmin):
    """Admin configuration for InterventionPhoto model."""
    
    list_display = ['intervention', 'caption', 'location', 'is_before', 'is_after', 'taken_at']
    list_filter = ['is_before', 'is_after', 'taken_at']
    search_fields = ['intervention__intervention_id', 'caption', 'location']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('intervention')


@admin.register(TechnicianAvailability)
class TechnicianAvailabilityAdmin(admin.ModelAdmin):
    """Admin configuration for TechnicianAvailability model."""
    
    list_display = ['technician', 'date', 'start_time', 'end_time', 'is_available', 'notes']
    list_filter = ['is_available', 'date', 'technician']
    search_fields = ['technician__username', 'technician__first_name', 'technician__last_name', 'notes']
    list_editable = ['is_available']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('technician')


@admin.register(InterventionReport)
class InterventionReportAdmin(admin.ModelAdmin):
    """Admin configuration for InterventionReport model."""
    
    list_display = ['intervention', 'report_type', 'title', 'created_by', 'created_at']
    list_filter = ['report_type', 'created_at']
    search_fields = ['intervention__intervention_id', 'title', 'summary']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('intervention', 'report_type', 'title')
        }),
        ('Contenu', {
            'fields': ('content', 'summary', 'recommendations', 'next_steps')
        }),
        ('Fichier', {
            'fields': ('pdf_file',)
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('intervention', 'created_by')