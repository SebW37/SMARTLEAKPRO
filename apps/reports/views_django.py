from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import InterventionReport, ReportTemplate


@login_required
def report_list(request):
    """Display list of intervention reports"""
    reports = InterventionReport.objects.filter(created_by=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(reports, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'reports': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'reports/report_list.html', context)


@login_required
def report_detail(request, report_id):
    """Display detailed view of a report"""
    report = get_object_or_404(InterventionReport, id=report_id, created_by=request.user)
    
    context = {
        'report': report,
    }
    return render(request, 'reports/report_detail.html', context)


@login_required
def report_create(request):
    """Create a new intervention report"""
    templates = ReportTemplate.objects.filter(is_active=True)
    
    if request.method == 'POST':
        # Handle form submission
        template_id = request.POST.get('template')
        title = request.POST.get('title')
        
        if template_id and title:
            template = get_object_or_404(ReportTemplate, id=template_id)
            report = InterventionReport.objects.create(
                intervention_id=request.POST.get('intervention'),
                template=template,
                title=title,
                created_by=request.user
            )
            return redirect('reports:report_edit', report_id=report.id)
    
    context = {
        'templates': templates,
    }
    return render(request, 'reports/report_create.html', context)


@login_required
def report_edit(request, report_id):
    """Edit an intervention report"""
    report = get_object_or_404(InterventionReport, id=report_id, created_by=request.user)
    
    if request.method == 'POST':
        # Handle form submission
        report.title = request.POST.get('title', report.title)
        report.save()
        return redirect('reports:report_list')
    
    context = {
        'report': report,
    }
    return render(request, 'reports/report_edit.html', context)


@login_required
def report_preview(request, report_id):
    """Preview a report"""
    report = get_object_or_404(InterventionReport, id=report_id, created_by=request.user)
    
    context = {
        'report': report,
    }
    return render(request, 'reports/report_preview.html', context)


@login_required
def template_list(request):
    """Display list of report templates"""
    templates = ReportTemplate.objects.filter(
        models.Q(is_public=True) | models.Q(created_by=request.user)
    ).order_by('-created_at')
    
    context = {
        'templates': templates,
    }
    return render(request, 'reports/template_list.html', context)


@login_required
def template_detail(request, template_id):
    """Display detailed view of a template"""
    template = get_object_or_404(ReportTemplate, id=template_id)
    
    # Check if user has access to this template
    if not template.is_public and template.created_by != request.user:
        raise Http404("Template not found")
    
    context = {
        'template': template,
    }
    return render(request, 'reports/template_detail.html', context)
