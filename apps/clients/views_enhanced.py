"""
Enhanced web views for client management.
Comprehensive CRUD operations and advanced features.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import csv
from datetime import datetime, timedelta

from .models import (
    Client, ClientSite, ClientContact, ClientContract, 
    ClientDocument, ClientNotification, ClientActivityLog
)


@login_required
def client_list_view(request):
    """Enhanced client list view with search, filtering, and pagination."""
    # Get search parameters
    search = request.GET.get('search', '')
    client_type = request.GET.get('type', '')
    status = request.GET.get('status', '')
    sort_by = request.GET.get('sort', 'name')
    
    # Build queryset
    clients = Client.objects.all()
    
    # Apply filters
    if search:
        clients = clients.filter(
            Q(name__icontains=search) |
            Q(client_number__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search) |
            Q(city__icontains=search) |
            Q(siret__icontains=search)
        )
    
    if client_type:
        clients = clients.filter(client_type=client_type)
    
    if status:
        clients = clients.filter(status=status)
    
    # Apply sorting
    if sort_by == 'name':
        clients = clients.order_by('name')
    elif sort_by == 'created':
        clients = clients.order_by('-created_at')
    elif sort_by == 'type':
        clients = clients.order_by('client_type', 'name')
    elif sort_by == 'status':
        clients = clients.order_by('status', 'name')
    
    # Pagination
    paginator = Paginator(clients, 25)  # 25 clients per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get statistics
    stats = {
        'total_clients': Client.objects.count(),
        'active_clients': Client.objects.filter(status='active').count(),
        'prospects': Client.objects.filter(status='prospect').count(),
        'companies': Client.objects.filter(client_type='company').count(),
        'individuals': Client.objects.filter(client_type='individual').count(),
    }
    
    context = {
        'clients': page_obj,
        'stats': stats,
        'search': search,
        'client_type': client_type,
        'status': status,
        'sort_by': sort_by,
        'client_types': Client.CLIENT_TYPE_CHOICES,
        'status_choices': Client.STATUS_CHOICES,
    }
    
    return render(request, 'clients.html', context)


@login_required
def client_detail_view(request, client_id):
    """Detailed client view with all related information."""
    client = get_object_or_404(Client, id=client_id)
    
    # Get related data
    contacts = client.contacts.all()
    contracts = client.contracts.all()
    sites = client.sites.all()
    documents = client.documents.all()
    notifications = client.notifications.all()[:10]  # Last 10 notifications
    activity_logs = client.activity_logs.all()[:20]  # Last 20 activities
    
    # Get recent interventions (if interventions app is available)
    recent_interventions = []
    try:
        from apps.interventions.models import Intervention
        recent_interventions = Intervention.objects.filter(
            client=client
        ).order_by('-created_at')[:5]
    except ImportError:
        pass
    
    # Log view activity
    ClientActivityLog.objects.create(
        client=client,
        action='viewed',
        description=f'Client profile viewed by {request.user.username}',
        user=request.user,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT')
    )
    
    context = {
        'client': client,
        'contacts': contacts,
        'contracts': contracts,
        'sites': sites,
        'documents': documents,
        'notifications': notifications,
        'activity_logs': activity_logs,
        'recent_interventions': recent_interventions,
    }
    
    return render(request, 'clients/client_detail.html', context)


@login_required
def client_create_view(request):
    """Create new client."""
    if request.method == 'POST':
        # Handle form submission
        form_data = request.POST.copy()
        client = Client.objects.create(
            name=form_data.get('name'),
            client_type=form_data.get('client_type', 'individual'),
            status=form_data.get('status', 'active'),
            email=form_data.get('email'),
            phone=form_data.get('phone'),
            address=form_data.get('address'),
            city=form_data.get('city'),
            postal_code=form_data.get('postal_code'),
            country=form_data.get('country', 'France'),
            notes=form_data.get('notes'),
            created_by=request.user
        )
        
        # Log creation activity
        ClientActivityLog.objects.create(
            client=client,
            action='created',
            description=f'Client created by {request.user.username}',
            user=request.user,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        
        messages.success(request, f'Client {client.name} created successfully.')
        return redirect('client_detail', client_id=client.id)
    
    return render(request, 'clients/client_form.html', {'title': 'Create Client'})


@login_required
def client_edit_view(request, client_id):
    """Edit existing client."""
    client = get_object_or_404(Client, id=client_id)
    
    if request.method == 'POST':
        # Store old values for activity log
        old_values = {
            'name': client.name,
            'email': client.email,
            'phone': client.phone,
            'status': client.status,
        }
        
        # Update client
        client.name = request.POST.get('name', client.name)
        client.client_type = request.POST.get('client_type', client.client_type)
        client.status = request.POST.get('status', client.status)
        client.email = request.POST.get('email', client.email)
        client.phone = request.POST.get('phone', client.phone)
        client.address = request.POST.get('address', client.address)
        client.city = request.POST.get('city', client.city)
        client.postal_code = request.POST.get('postal_code', client.postal_code)
        client.country = request.POST.get('country', client.country)
        client.notes = request.POST.get('notes', client.notes)
        client.save()
        
        # Store new values for activity log
        new_values = {
            'name': client.name,
            'email': client.email,
            'phone': client.phone,
            'status': client.status,
        }
        
        # Log update activity
        ClientActivityLog.objects.create(
            client=client,
            action='updated',
            description=f'Client updated by {request.user.username}',
            user=request.user,
            old_values=old_values,
            new_values=new_values,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        
        messages.success(request, f'Client {client.name} updated successfully.')
        return redirect('client_detail', client_id=client.id)
    
    return render(request, 'clients/client_form.html', {
        'title': 'Edit Client',
        'client': client
    })


@login_required
def client_delete_view(request, client_id):
    """Delete client (soft delete by setting is_active=False)."""
    client = get_object_or_404(Client, id=client_id)
    
    if request.method == 'POST':
        # Soft delete
        client.is_active = False
        client.status = 'archived'
        client.save()
        
        # Log deletion activity
        ClientActivityLog.objects.create(
            client=client,
            action='deleted',
            description=f'Client deactivated by {request.user.username}',
            user=request.user,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        
        messages.success(request, f'Client {client.name} has been deactivated.')
        return redirect('client_list')
    
    return render(request, 'clients/client_confirm_delete.html', {'client': client})


@login_required
def client_export_view(request):
    """Export clients to CSV."""
    # Get filter parameters
    search = request.GET.get('search', '')
    client_type = request.GET.get('type', '')
    status = request.GET.get('status', '')
    
    # Build queryset
    clients = Client.objects.all()
    
    if search:
        clients = clients.filter(
            Q(name__icontains=search) |
            Q(client_number__icontains=search) |
            Q(email__icontains=search)
        )
    
    if client_type:
        clients = clients.filter(client_type=client_type)
    
    if status:
        clients = clients.filter(status=status)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="clients_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Numéro Client', 'Nom', 'Type', 'Statut', 'Email', 'Téléphone',
        'Adresse', 'Ville', 'Code Postal', 'SIRET', 'SIREN',
        'Type Contrat', 'Date Création'
    ])
    
    for client in clients:
        writer.writerow([
            client.client_number,
            client.name,
            client.get_client_type_display(),
            client.get_status_display(),
            client.email or '',
            client.phone or '',
            client.address,
            client.city,
            client.postal_code,
            client.siret or '',
            client.siren or '',
            client.get_contract_type_display() if client.contract_type else '',
            client.created_at.strftime('%d/%m/%Y %H:%M')
        ])
    
    return response


@login_required
def client_stats_view(request):
    """Get client statistics for dashboard."""
    stats = {
        'total_clients': Client.objects.count(),
        'active_clients': Client.objects.filter(status='active').count(),
        'prospects': Client.objects.filter(status='prospect').count(),
        'companies': Client.objects.filter(client_type='company').count(),
        'individuals': Client.objects.filter(client_type='individual').count(),
        'public_clients': Client.objects.filter(client_type='public').count(),
        'syndics': Client.objects.filter(client_type='syndic').count(),
        'recent_clients': Client.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).count(),
    }
    
    return JsonResponse(stats)


@login_required
@csrf_exempt
def client_ajax_view(request):
    """Handle AJAX requests for client operations."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')
            client_id = data.get('client_id')
            
            if action == 'toggle_status':
                client = get_object_or_404(Client, id=client_id)
                client.is_active = not client.is_active
                client.save()
                
                return JsonResponse({
                    'success': True,
                    'is_active': client.is_active,
                    'message': f'Client {client.name} {"activated" if client.is_active else "deactivated"}'
                })
            
            elif action == 'get_contacts':
                client = get_object_or_404(Client, id=client_id)
                contacts = list(client.contacts.values(
                    'id', 'first_name', 'last_name', 'role', 'email', 'phone', 'is_primary'
                ))
                return JsonResponse({'success': True, 'contacts': contacts})
            
            elif action == 'get_contracts':
                client = get_object_or_404(Client, id=client_id)
                contracts = list(client.contracts.values(
                    'id', 'contract_number', 'contract_type', 'status', 
                    'start_date', 'end_date', 'monthly_amount'
                ))
                return JsonResponse({'success': True, 'contracts': contracts})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})
