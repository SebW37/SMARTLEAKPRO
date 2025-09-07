"""
URL configuration for SmartLeakPro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse


def home(request):
    """Home view with statistics."""
    from apps.clients.models import Client, ClientSite
    from django.shortcuts import render
    
    total_clients = Client.objects.filter(is_active=True).count()
    total_sites = ClientSite.objects.filter(is_active=True).count()
    
    return render(request, 'home.html', {
        'total_clients': total_clients,
        'total_sites': total_sites,
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('clients/', include('apps.clients.urls')),
    path('interventions/', include('apps.interventions.urls')),
    path('reports/', include('apps.reports.urls_simple')),
    path('api/', include('apps.reports.urls')),
]
