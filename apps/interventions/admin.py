"""
Admin configuration for intervention models.
"""
from django.contrib import admin
from .models import Intervention, InterventionTask, InterventionDocument, InterventionNote


@admin.register(Intervention)
class InterventionAdmin(admin.ModelAdmin):
    """Admin configuration for Intervention model."""
    
    list_display = [
        'title', 'client', 'site', 'intervention_type', 'status', 'priority',
        'scheduled_date', 'assigned_technician', 'is_overdue'
    ]
    list_filter = ['status', 'priority', 'intervention_type', 'scheduled_date', 'created_at']
    search_fields = ['title', 'description', 'client__name', 'site__name']
    ordering = ['-scheduled_date']
    readonly_fields = ['created_at', 'updated_at', 'is_overdue', 'duration']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'description', 'intervention_type', 'status', 'priority')
        }),
        ('Client et site', {
            'fields': ('client', 'site', 'location', 'address')
        }),
        ('Planification', {
            'fields': ('scheduled_date', 'estimated_duration', 'assigned_technician')
        }),
        ('Exécution', {
            'fields': ('actual_start_date', 'actual_end_date')
        }),
        ('Détails', {
            'fields': ('notes', 'materials_needed', 'special_instructions')
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


@admin.register(InterventionTask)
class InterventionTaskAdmin(admin.ModelAdmin):
    """Admin configuration for InterventionTask model."""
    
    list_display = [
        'title', 'intervention', 'status', 'assigned_to', 'order', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description', 'intervention__title']
    ordering = ['intervention', 'order']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(InterventionDocument)
class InterventionDocumentAdmin(admin.ModelAdmin):
    """Admin configuration for InterventionDocument model."""
    
    list_display = [
        'title', 'intervention', 'task', 'document_type', 'uploaded_by', 'uploaded_at'
    ]
    list_filter = ['document_type', 'uploaded_at']
    search_fields = ['title', 'description', 'intervention__title']
    ordering = ['-uploaded_at']
    readonly_fields = ['uploaded_at']


@admin.register(InterventionNote)
class InterventionNoteAdmin(admin.ModelAdmin):
    """Admin configuration for InterventionNote model."""
    
    list_display = [
        'title', 'intervention', 'task', 'is_internal', 'created_by', 'created_at'
    ]
    list_filter = ['is_internal', 'created_at']
    search_fields = ['title', 'content', 'intervention__title']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
