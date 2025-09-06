"""
Views for clients app.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import Client, ClientSite


def client_list(request):
    """List all clients."""
    clients = Client.objects.all()
    return render(request, 'clients/client_list.html', {'clients': clients})


def client_detail(request, client_id):
    """Show client details."""
    client = get_object_or_404(Client, id=client_id)
    sites = client.sites.all()
    return render(request, 'clients/client_detail.html', {
        'client': client,
        'sites': sites
    })


def user_list(request):
    """List all users."""
    users = User.objects.all()
    return render(request, 'users/user_list.html', {'users': users})