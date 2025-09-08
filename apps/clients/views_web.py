"""
Web views for client management.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Client

@login_required
def client_list_view(request):
    """Client list view with user-friendly interface."""
    clients = Client.objects.all().order_by('name')
    return render(request, 'clients.html', {'clients': clients})
