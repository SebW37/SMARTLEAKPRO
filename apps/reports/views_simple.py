from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


def test_view(request):
    """Test view for reports page"""
    context = {
        'page_title': 'Rapports d\'Intervention - Test',
        'message': 'Cette page fonctionne ! Le module de rapports est en cours de développement.',
        'success_message': 'Module de rapports chargé avec succès',
        'description': 'Le système de rapports d\'intervention est maintenant opérationnel.'
    }
    return render(request, 'reports/report_list.html', context)


def report_list(request):
    """List all reports"""
    # Mock data for now
    reports = [
        {
            'id': 1,
            'title': 'Rapport d\'inspection - Site A',
            'client': 'Client ABC',
            'site': 'Site Principal',
            'status': 'draft',
            'created_at': '2025-09-07',
            'created_by': 'Technicien 1'
        },
        {
            'id': 2,
            'title': 'Rapport d\'urgence - Fuite majeure',
            'client': 'Client XYZ',
            'site': 'Site Secondaire',
            'status': 'completed',
            'created_at': '2025-09-06',
            'created_by': 'Technicien 2'
        },
        {
            'id': 3,
            'title': 'Rapport de maintenance préventive',
            'client': 'Client DEF',
            'site': 'Site Industriel',
            'status': 'in_progress',
            'created_at': '2025-09-05',
            'created_by': 'Technicien 3'
        }
    ]
    
    context = {
        'page_title': 'Rapports d\'Intervention',
        'reports': reports,
        'total_reports': len(reports)
    }
    return render(request, 'reports/report_list.html', context)


def report_create(request):
    """Create a new report"""
    if request.method == 'POST':
        # Handle form submission
        title = request.POST.get('title', '')
        client = request.POST.get('client', '')
        site = request.POST.get('site', '')
        description = request.POST.get('description', '')
        
        if title and client:
            messages.success(request, f'Rapport "{title}" créé avec succès!')
            return redirect('reports:report_list')
        else:
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
    
    context = {
        'page_title': 'Créer un Rapport',
        'form_title': 'Nouveau Rapport d\'Intervention'
    }
    return render(request, 'reports/report_create.html', context)


def report_detail(request, report_id):
    """View report details"""
    # Mock data for now
    report = {
        'id': report_id,
        'title': 'Rapport d\'inspection - Site A',
        'client': 'Client ABC',
        'site': 'Site Principal',
        'status': 'draft',
        'created_at': '2025-09-07',
        'created_by': 'Technicien 1',
        'description': 'Rapport détaillé de l\'inspection effectuée sur le site principal.',
        'sections': [
            {'title': 'Informations générales', 'type': 'text', 'value': 'Inspection de routine'},
            {'title': 'État des équipements', 'type': 'checklist', 'value': 'Tous les équipements fonctionnent correctement'},
            {'title': 'Photos', 'type': 'photo', 'value': '3 photos ajoutées'},
            {'title': 'Recommandations', 'type': 'textarea', 'value': 'Aucune action corrective nécessaire'}
        ]
    }
    
    context = {
        'page_title': f'Rapport #{report_id}',
        'report': report
    }
    return render(request, 'reports/report_detail.html', context)


def report_edit(request, report_id):
    """Edit a report"""
    if request.method == 'POST':
        # Handle form submission
        title = request.POST.get('title', '')
        client = request.POST.get('client', '')
        site = request.POST.get('site', '')
        description = request.POST.get('description', '')
        
        if title and client:
            messages.success(request, f'Rapport "{title}" modifié avec succès!')
            return redirect('reports:report_detail', report_id=report_id)
        else:
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
    
    # Mock data for now
    report = {
        'id': report_id,
        'title': 'Rapport d\'inspection - Site A',
        'client': 'Client ABC',
        'site': 'Site Principal',
        'description': 'Rapport détaillé de l\'inspection effectuée sur le site principal.'
    }
    
    context = {
        'page_title': f'Modifier le Rapport #{report_id}',
        'report': report
    }
    return render(request, 'reports/report_edit.html', context)


def template_list(request):
    """List report templates"""
    # Mock data for now
    templates = [
        {
            'id': 1,
            'name': 'Inspection Standard',
            'description': 'Template pour les inspections de routine',
            'type': 'standard',
            'sections_count': 8,
            'is_active': True
        },
        {
            'id': 2,
            'name': 'Urgence Fuite',
            'description': 'Template pour les interventions d\'urgence',
            'type': 'emergency',
            'sections_count': 12,
            'is_active': True
        },
        {
            'id': 3,
            'name': 'Maintenance Préventive',
            'description': 'Template pour la maintenance préventive',
            'type': 'maintenance',
            'sections_count': 6,
            'is_active': True
        }
    ]
    
    context = {
        'page_title': 'Modèles de Rapports',
        'templates': templates,
        'total_templates': len(templates)
    }
    return render(request, 'reports/template_list.html', context)


def template_detail(request, template_id):
    """View template details"""
    # Mock data for now
    template = {
        'id': template_id,
        'name': 'Inspection Standard',
        'description': 'Template pour les inspections de routine',
        'type': 'standard',
        'sections': [
            {'title': 'Informations générales', 'type': 'text', 'required': True},
            {'title': 'État des équipements', 'type': 'checklist', 'required': True},
            {'title': 'Photos', 'type': 'photo', 'required': False},
            {'title': 'Recommandations', 'type': 'textarea', 'required': False}
        ]
    }
    
    context = {
        'page_title': f'Modèle: {template["name"]}',
        'template': template
    }
    return render(request, 'reports/template_detail.html', context)