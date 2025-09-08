"""
Views for interventions app.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Intervention, LeakType, Equipment, TechnicianAvailability


def intervention_list(request):
    """List all interventions with filtering."""
    interventions = Intervention.objects.select_related('client', 'site', 'technician').all()
    
    # Filtres
    status_filter = request.GET.get('status', '')
    technician_filter = request.GET.get('technician', '')
    priority_filter = request.GET.get('priority', '')
    date_filter = request.GET.get('date', '')
    
    if status_filter:
        interventions = interventions.filter(status=status_filter)
    if technician_filter:
        interventions = interventions.filter(technician_id=technician_filter)
    if priority_filter:
        interventions = interventions.filter(priority=priority_filter)
    if date_filter:
        interventions = interventions.filter(scheduled_date__date=date_filter)
    
    # Techniciens pour le filtre
    technicians = User.objects.filter(groups__name='Techniciens').order_by('first_name', 'last_name')
    
    context = {
        'interventions': interventions,
        'technicians': technicians,
        'status_choices': Intervention.STATUS_CHOICES,
        'priority_choices': Intervention.PRIORITY_CHOICES,
        'current_filters': {
            'status': status_filter,
            'technician': technician_filter,
            'priority': priority_filter,
            'date': date_filter,
        }
    }
    
    return render(request, 'interventions/intervention_list.html', context)


def intervention_detail(request, intervention_id):
    """Show intervention details."""
    intervention = get_object_or_404(
        Intervention.objects.select_related('client', 'site', 'technician'),
        intervention_id=intervention_id
    )
    
    photos = intervention.photos.all().order_by('-taken_at')
    reports = intervention.reports.all().order_by('-created_at')
    
    context = {
        'intervention': intervention,
        'photos': photos,
        'reports': reports,
    }
    
    return render(request, 'interventions/intervention_detail.html', context)


def intervention_calendar(request):
    """Calendar view for interventions."""
    # Récupérer le mois et l'année depuis les paramètres
    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))
    
    # Calculer les dates du mois
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    # Récupérer les interventions du mois
    interventions = Intervention.objects.filter(
        scheduled_date__gte=start_date,
        scheduled_date__lt=end_date
    ).select_related('client', 'site', 'technician').order_by('scheduled_date')
    
    # Grouper par jour
    interventions_by_day = {}
    for intervention in interventions:
        day = intervention.scheduled_date.day
        if day not in interventions_by_day:
            interventions_by_day[day] = []
        interventions_by_day[day].append(intervention)
    
    # Navigation mois
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    context = {
        'year': year,
        'month': month,
        'interventions_by_day': interventions_by_day,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'month_names': [
            'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
            'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
        ]
    }
    
    return render(request, 'interventions/intervention_calendar.html', context)


def technician_dashboard(request, technician_id):
    """Dashboard pour un technicien spécifique."""
    technician = get_object_or_404(User, id=technician_id)
    
    # Interventions du jour
    today = timezone.now().date()
    today_interventions = Intervention.objects.filter(
        technician=technician,
        scheduled_date__date=today
    ).order_by('scheduled_date')
    
    # Interventions de la semaine
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    week_interventions = Intervention.objects.filter(
        technician=technician,
        scheduled_date__date__range=[week_start, week_end]
    ).order_by('scheduled_date')
    
    # Statistiques
    total_interventions = Intervention.objects.filter(technician=technician).count()
    completed_interventions = Intervention.objects.filter(
        technician=technician, 
        status='completed'
    ).count()
    
    context = {
        'technician': technician,
        'today_interventions': today_interventions,
        'week_interventions': week_interventions,
        'total_interventions': total_interventions,
        'completed_interventions': completed_interventions,
    }
    
    return render(request, 'interventions/technician_dashboard.html', context)


def equipment_list(request):
    """List all equipment."""
    equipment = Equipment.objects.all()
    
    # Filtres
    category_filter = request.GET.get('category', '')
    available_filter = request.GET.get('available', '')
    
    if category_filter:
        equipment = equipment.filter(category=category_filter)
    if available_filter == 'true':
        equipment = equipment.filter(available=True)
    elif available_filter == 'false':
        equipment = equipment.filter(available=False)
    
    context = {
        'equipment': equipment,
        'category_choices': Equipment.CATEGORY_CHOICES,
        'current_filters': {
            'category': category_filter,
            'available': available_filter,
        }
    }
    
    return render(request, 'interventions/equipment_list.html', context)