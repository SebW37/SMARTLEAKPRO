from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
import uuid

# Mock data for demonstration
mock_reports = [
    {
        'id': '550e8400-e29b-41d4-a716-446655440000',
        'title': 'Rapport d\'Intervention #2025-001',
        'status': 'draft',
        'created_at': timezone.now() - timezone.timedelta(days=5),
        'template_name': 'Standard Leak Detection',
        'client_name': 'Client A',
        'intervention_date': '2025-09-01',
    },
    {
        'id': '550e8400-e29b-41d4-a716-446655440001',
        'title': 'Rapport d\'Intervention #2025-002',
        'status': 'in_progress',
        'created_at': timezone.now() - timezone.timedelta(days=3),
        'template_name': 'Emergency Repair',
        'client_name': 'Client B',
        'intervention_date': '2025-09-03',
    },
    {
        'id': '550e8400-e29b-41d4-a716-446655440002',
        'title': 'Rapport d\'Intervention #2025-003',
        'status': 'pending_review',
        'created_at': timezone.now() - timezone.timedelta(days=1),
        'template_name': 'Annual Inspection',
        'client_name': 'Client C',
        'intervention_date': '2025-09-05',
    },
]

mock_templates = [
    {'id': '550e8400-e29b-41d4-a716-446655440010', 'name': 'Standard Leak Detection', 'type': 'standard', 'is_active': True},
    {'id': '550e8400-e29b-41d4-a716-446655440011', 'name': 'Emergency Repair', 'type': 'emergency', 'is_active': True},
    {'id': '550e8400-e29b-41d4-a716-446655440012', 'name': 'Annual Inspection', 'type': 'inspection', 'is_active': False},
]

def report_list(request):
    context = {
        'reports': mock_reports,
        'message': "Module de rapports chargé avec succès",
        'message_type': 'success'
    }
    return render(request, 'reports/report_list.html', context)

def report_create(request):
    context = {
        'templates': mock_templates,
        'message': "Formulaire de création de rapport",
        'message_type': 'info'
    }
    return render(request, 'reports/report_create.html', context)

def report_detail(request, pk):
    report = next((r for r in mock_reports if str(r['id']) == pk), None)
    context = {
        'report': report,
        'message': f"Détails du rapport {pk}",
        'message_type': 'info'
    }
    return render(request, 'reports/report_detail.html', context)

def report_edit(request, pk):
    report = next((r for r in mock_reports if str(r['id']) == pk), None)
    context = {
        'report': report,
        'templates': mock_templates,
        'message': f"Modification du rapport {pk}",
        'message_type': 'info'
    }
    return render(request, 'reports/report_edit.html', context)

def template_list(request):
    context = {
        'templates': mock_templates,
        'message': "Liste des modèles de rapports",
        'message_type': 'info'
    }
    return render(request, 'reports/template_list.html', context)

def template_detail(request, pk):
    template = next((t for t in mock_templates if str(t['id']) == pk), None)
    context = {
        'template': template,
        'message': f"Détails du modèle {pk}",
        'message_type': 'info'
    }
    return render(request, 'reports/template_detail.html', context)
