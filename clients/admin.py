"""
Admin configuration for clients app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django import forms
from .models import Client, ClientSite
from .forms import SimpleUserCreationForm


class CustomUserAdmin(UserAdmin):
    """Custom user admin with simplified validation."""
    
    add_form = SimpleUserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password'),
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        """Use custom form for adding users."""
        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Admin configuration for Client model."""
    
    list_display = ['name', 'client_type', 'city', 'email', 'is_active', 'created_at']
    list_filter = ['client_type', 'is_active', 'created_at']
    search_fields = ['name', 'email', 'city']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'client_type', 'is_active')
        }),
        ('Contact', {
            'fields': ('email', 'phone')
        }),
        ('Adresse', {
            'fields': ('address', 'city', 'postal_code', 'country')
        }),
        ('Géolocalisation', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ClientSite)
class ClientSiteAdmin(admin.ModelAdmin):
    """Admin configuration for ClientSite model."""
    
    list_display = ['name', 'client', 'city', 'contact_name', 'is_active']
    list_filter = ['is_active', 'client', 'created_at']
    search_fields = ['name', 'client__name', 'city', 'contact_name']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('client', 'name', 'description', 'is_active')
        }),
        ('Adresse', {
            'fields': ('address', 'city', 'postal_code', 'country')
        }),
        ('Géolocalisation', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Contact', {
            'fields': ('contact_name', 'contact_phone', 'contact_email')
        }),
        ('Informations supplémentaires', {
            'fields': ('access_instructions', 'notes'),
            'classes': ('collapse',)
        }),
    )