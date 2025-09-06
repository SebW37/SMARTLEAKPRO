"""
Client admin configuration.
"""
from django.contrib import admin
from .models import Client, ClientSite, ClientDocument


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Client admin."""
    
    list_display = ('name', 'client_type', 'email', 'city', 'is_active', 'created_at')
    list_filter = ('client_type', 'is_active', 'created_at')
    search_fields = ('name', 'email', 'city')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ClientSite)
class ClientSiteAdmin(admin.ModelAdmin):
    """Client site admin."""
    
    list_display = ('name', 'client', 'city', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'client__name', 'city')


@admin.register(ClientDocument)
class ClientDocumentAdmin(admin.ModelAdmin):
    """Client document admin."""
    
    list_display = ('title', 'client', 'document_type', 'uploaded_at')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = ('title', 'client__name')