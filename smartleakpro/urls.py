"""
URL configuration for SmartLeakPro project.
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.http import HttpResponse

def home_view(request):
    """Home view with statistics."""
    # Get statistics
    from apps.clients.models import Client, ClientSite
    from apps.interventions.models import Intervention
    from apps.reports.models import InterventionReport
    
    stats = {
        'total_clients': Client.objects.filter(is_active=True).count(),
        'total_sites': ClientSite.objects.filter(is_active=True).count(),
        'total_interventions': Intervention.objects.count(),
        'total_reports': InterventionReport.objects.count(),
    }
    
    return render(request, 'home.html', stats)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/clients/', include('apps.clients.urls')),
    path('api/interventions/', include('apps.interventions.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/inspections/', include('apps.inspections.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('clients/', include('apps.clients.urls')),
    path('interventions/', include('apps.interventions.urls')),
    path('reports/', include('apps.reports.urls')),
    path('', home_view, name='home'),
]
