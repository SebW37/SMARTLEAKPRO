"""
Client admin configuration.
"""
from django.contrib import admin
from .models import (
    Client, ClientSite, ClientContact, ClientContract, 
    ClientDocument, ClientNotification, ClientActivityLog
)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Client admin."""
    
    list_display = ('client_number', 'name', 'client_type', 'status', 'email', 'phone', 'city', 'is_active', 'created_at')
    list_filter = ('client_type', 'status', 'is_active', 'created_at', 'contract_type')
    search_fields = ('client_number', 'name', 'email', 'phone', 'city', 'siret', 'siren')
    readonly_fields = ('client_number', 'created_at', 'updated_at')
    fieldsets = (
        ('Informations générales', {
            'fields': ('client_number', 'name', 'client_type', 'status', 'is_active')
        }),
        ('Contact', {
            'fields': ('email', 'phone', 'secondary_email', 'secondary_phone')
        }),
        ('Adresse', {
            'fields': ('address', 'city', 'postal_code', 'country', 'latitude', 'longitude')
        }),
        ('Contrat', {
            'fields': ('contract_type', 'contract_start_date', 'contract_end_date')
        }),
        ('Facturation', {
            'fields': ('billing_address', 'billing_city', 'billing_postal_code', 'siret', 'siren', 'vat_number', 'preferred_payment_method', 'bank_details')
        }),
        ('Préférences de visite', {
            'fields': ('visit_preferences', 'access_constraints', 'preferred_visit_days', 'preferred_visit_hours')
        }),
        ('RGPD', {
            'fields': ('gdpr_consent', 'gdpr_consent_date', 'data_retention_until')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ClientSite)
class ClientSiteAdmin(admin.ModelAdmin):
    """Client site admin."""
    
    list_display = ('name', 'client', 'city', 'contact_name', 'is_active')
    list_filter = ('is_active', 'city')
    search_fields = ('name', 'client__name', 'contact_name')


@admin.register(ClientContact)
class ClientContactAdmin(admin.ModelAdmin):
    """Client contact admin."""
    
    list_display = ('first_name', 'last_name', 'client', 'role', 'position', 'email', 'phone', 'is_primary', 'is_active')
    list_filter = ('role', 'is_primary', 'is_active')
    search_fields = ('first_name', 'last_name', 'client__name', 'email', 'phone')


@admin.register(ClientContract)
class ClientContractAdmin(admin.ModelAdmin):
    """Client contract admin."""
    
    list_display = ('contract_number', 'client', 'contract_type', 'status', 'start_date', 'end_date', 'monthly_amount')
    list_filter = ('contract_type', 'status', 'start_date')
    search_fields = ('contract_number', 'client__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ClientDocument)
class ClientDocumentAdmin(admin.ModelAdmin):
    """Client document admin."""
    
    list_display = ('title', 'client', 'document_type', 'uploaded_by', 'uploaded_at', 'is_public')
    list_filter = ('document_type', 'is_public', 'uploaded_at')
    search_fields = ('title', 'client__name', 'description')


@admin.register(ClientNotification)
class ClientNotificationAdmin(admin.ModelAdmin):
    """Client notification admin."""
    
    list_display = ('client', 'notification_type', 'status', 'subject', 'sent_to', 'sent_at')
    list_filter = ('notification_type', 'status', 'sent_at')
    search_fields = ('client__name', 'subject', 'sent_to')


@admin.register(ClientActivityLog)
class ClientActivityLogAdmin(admin.ModelAdmin):
    """Client activity log admin."""
    
    list_display = ('client', 'action', 'user', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('client__name', 'description')
    readonly_fields = ('created_at',)