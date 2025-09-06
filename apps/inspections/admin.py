"""
Admin configuration for inspection models.
"""
from django.contrib import admin
from .models import (
    InspectionTemplate, Inspection, InspectionItem, 
    InspectionMedia, InspectionSignature
)


@admin.register(InspectionTemplate)
class InspectionTemplateAdmin(admin.ModelAdmin):
    """Admin configuration for InspectionTemplate model."""
    
    list_display = ['name', 'category', 'is_active', 'created_by', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    """Admin configuration for Inspection model."""
    
    list_display = [
        'title', 'client', 'site', 'status', 'inspector', 'inspection_date',
        'score', 'compliance_status', 'duration'
    ]
    list_filter = ['status', 'inspection_date', 'created_at', 'compliance_status']
    search_fields = ['title', 'description', 'client__name', 'site__name']
    ordering = ['-inspection_date']
    readonly_fields = ['created_at', 'updated_at', 'duration', 'score_percentage']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'description', 'status', 'template', 'form_data')
        }),
        ('Client et site', {
            'fields': ('client', 'site', 'intervention', 'location', 'address')
        }),
        ('Planification', {
            'fields': ('inspection_date', 'inspector', 'created_by')
        }),
        ('Exécution', {
            'fields': ('started_at', 'completed_at')
        }),
        ('Résultats', {
            'fields': ('score', 'max_score', 'compliance_status', 'score_percentage')
        }),
        ('Détails', {
            'fields': ('notes', 'recommendations')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(InspectionItem)
class InspectionItemAdmin(admin.ModelAdmin):
    """Admin configuration for InspectionItem model."""
    
    list_display = [
        'label', 'inspection', 'item_type', 'is_required', 'order', 'created_at'
    ]
    list_filter = ['item_type', 'is_required', 'created_at']
    search_fields = ['label', 'value', 'inspection__title']
    ordering = ['inspection', 'order']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(InspectionMedia)
class InspectionMediaAdmin(admin.ModelAdmin):
    """Admin configuration for InspectionMedia model."""
    
    list_display = [
        'title', 'inspection', 'item', 'media_type', 'uploaded_by', 'uploaded_at'
    ]
    list_filter = ['media_type', 'uploaded_at', 'captured_at']
    search_fields = ['title', 'description', 'inspection__title']
    ordering = ['-uploaded_at']
    readonly_fields = ['uploaded_at']


@admin.register(InspectionSignature)
class InspectionSignatureAdmin(admin.ModelAdmin):
    """Admin configuration for InspectionSignature model."""
    
    list_display = [
        'signer_name', 'signer_role', 'inspection', 'item', 'signed_at'
    ]
    list_filter = ['signer_role', 'signed_at', 'created_at']
    search_fields = ['signer_name', 'signer_role', 'inspection__title']
    ordering = ['-signed_at']
    readonly_fields = ['created_at']
