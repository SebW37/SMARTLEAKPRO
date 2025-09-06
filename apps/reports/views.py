"""
Views for report management.
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from .models import ReportTemplate, Report, ReportSchedule, ReportAnalytics
from .serializers import (
    ReportTemplateSerializer, ReportSerializer, ReportScheduleSerializer,
    ReportAnalyticsSerializer, ReportGenerationSerializer
)
from .tasks import generate_report_task


class ReportTemplateListCreateView(generics.ListCreateAPIView):
    """List and create report templates."""
    
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['template_type', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ReportTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a report template."""
    
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]


class ReportListCreateView(generics.ListCreateAPIView):
    """List and create reports."""
    
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'format', 'client', 'intervention', 'inspection', 'template']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'generated_at', 'title']
    ordering = ['-created_at']


class ReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a report."""
    
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]


class ReportScheduleListCreateView(generics.ListCreateAPIView):
    """List and create report schedules."""
    
    queryset = ReportSchedule.objects.all()
    serializer_class = ReportScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'frequency', 'template']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'next_run']
    ordering = ['name']


class ReportScheduleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a report schedule."""
    
    queryset = ReportSchedule.objects.all()
    serializer_class = ReportScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]


class ReportAnalyticsListView(generics.ListAPIView):
    """List report analytics."""
    
    queryset = ReportAnalytics.objects.all()
    serializer_class = ReportAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['report']
    search_fields = ['report__title']
    ordering_fields = ['view_count', 'download_count', 'created_at']
    ordering = ['-created_at']


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_report_view(request):
    """Generate a new report."""
    serializer = ReportGenerationSerializer(data=request.data)
    if serializer.is_valid():
        # Create report record
        report_data = serializer.validated_data.copy()
        report_data['created_by'] = request.user
        report_data['status'] = 'generating'
        
        report = Report.objects.create(**report_data)
        
        # Start background task
        generate_report_task.delay(report.id)
        
        return Response(
            {'message': 'Report generation started', 'report_id': report.id},
            status=status.HTTP_202_ACCEPTED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_report_view(request, pk):
    """Download a report file."""
    report = get_object_or_404(Report, pk=pk)
    
    if not report.file:
        raise Http404("Report file not found")
    
    # Track download
    analytics, created = ReportAnalytics.objects.get_or_create(report=report)
    analytics.download_count += 1
    analytics.downloaded_by.add(request.user)
    analytics.last_downloaded_at = timezone.now()
    if not analytics.first_downloaded_at:
        analytics.first_downloaded_at = timezone.now()
    analytics.save()
    
    # Return file
    response = HttpResponse(
        report.file.read(),
        content_type='application/octet-stream'
    )
    response['Content-Disposition'] = f'attachment; filename="{report.title}.{report.format}"'
    return response


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def view_report_view(request, pk):
    """View a report (track view)."""
    report = get_object_or_404(Report, pk=pk)
    
    # Track view
    analytics, created = ReportAnalytics.objects.get_or_create(report=report)
    analytics.view_count += 1
    analytics.viewed_by.add(request.user)
    analytics.last_viewed_at = timezone.now()
    if not analytics.first_viewed_at:
        analytics.first_viewed_at = timezone.now()
    analytics.save()
    
    serializer = ReportSerializer(report, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def report_stats_view(request):
    """Get report statistics."""
    stats = {
        'total_reports': Report.objects.count(),
        'generating_reports': Report.objects.filter(status='generating').count(),
        'completed_reports': Report.objects.filter(status='completed').count(),
        'failed_reports': Report.objects.filter(status='failed').count(),
        'total_templates': ReportTemplate.objects.filter(is_active=True).count(),
        'active_schedules': ReportSchedule.objects.filter(is_active=True).count(),
        'total_downloads': sum(ReportAnalytics.objects.values_list('download_count', flat=True)),
        'total_views': sum(ReportAnalytics.objects.values_list('view_count', flat=True)),
    }
    return Response(stats)
