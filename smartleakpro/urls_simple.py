"""
URL configuration for SmartLeakPro project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse


def home(request):
    """Home view with statistics."""
    from django.shortcuts import render

    return render(request, 'home.html', {
        'total_clients': 0,
        'total_sites': 0,
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('reports/', include('apps.reports.urls')),
    # path('clients/', include('apps.clients.urls')),
    # path('interventions/', include('apps.interventions.urls')),
    # path('api/', include('apps.reports.urls')),
]
