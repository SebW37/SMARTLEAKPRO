"""
Clients app configuration.
"""
from django.apps import AppConfig


class ClientsConfig(AppConfig):
    """Clients app configuration."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.clients'
    verbose_name = 'Clients'