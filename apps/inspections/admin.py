"""
Admin configuration for inspections app.
"""
from django.contrib import admin
from .models import InspectionTemplate, Inspection, InspectionItem, InspectionMedia, InspectionSignature


@admin.register(InspectionTemplate)
class InspectionTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'status', 'scheduled_date', 'inspector']
    list_filter = ['status', 'scheduled_date', 'client']
    search_fields = ['title', 'description', 'client__name']
    ordering = ['-scheduled_date']


@admin.register(InspectionItem)
class InspectionItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'inspection', 'is_checked']
    list_filter = ['is_checked', 'inspection__status']
    search_fields = ['name', 'description']
    ordering = ['inspection', 'name']


@admin.register(InspectionMedia)
class InspectionMediaAdmin(admin.ModelAdmin):
    list_display = ['title', 'inspection', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['title', 'description']
    ordering = ['-uploaded_at']


@admin.register(InspectionSignature)
class InspectionSignatureAdmin(admin.ModelAdmin):
    list_display = ['signer_name', 'inspection', 'signed_at']
    list_filter = ['signed_at']
    search_fields = ['signer_name']
    ordering = ['-signed_at']
