from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
from django.core.files.storage import default_storage
from django.utils import timezone
from django.db import transaction
import json
import os

from .models import (
    ReportTemplate, ReportSection, InterventionReport, 
    ReportSectionData, ReportMedia, ReportSignature, 
    ReportExport, ReportHistory
)
from .serializers import (
    ReportTemplateSerializer, ReportTemplateCreateSerializer,
    InterventionReportSerializer, ReportCreateSerializer, ReportUpdateSerializer,
    ReportSectionDataSerializer, ReportMediaSerializer, ReportMediaUploadSerializer,
    ReportSignatureSerializer, ReportSignatureCreateSerializer,
    ReportExportSerializer, ReportExportCreateSerializer,
    ReportHistorySerializer
)


class ReportTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing report templates"""
    queryset = ReportTemplate.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReportTemplateCreateSerializer
        return ReportTemplateSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            # Non-staff users can only see public templates and their own
            queryset = queryset.filter(
                models.Q(is_public=True) | models.Q(created_by=self.request.user)
            )
        return queryset
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a template with a new name"""
        template = self.get_object()
        new_name = request.data.get('name', f"{template.name} (Copy)")
        
        with transaction.atomic():
            # Create new template
            new_template = ReportTemplate.objects.create(
                name=new_name,
                description=template.description,
                template_type=template.template_type,
                is_active=template.is_active,
                is_public=False,  # Duplicated templates are private by default
                created_by=request.user,
                configuration=template.configuration
            )
            
            # Duplicate sections
            for section in template.sections.all():
                ReportSection.objects.create(
                    template=new_template,
                    title=section.title,
                    section_type=section.section_type,
                    order=section.order,
                    is_required=section.is_required,
                    is_conditional=section.is_conditional,
                    configuration=section.configuration,
                    condition_field=section.condition_field,
                    condition_value=section.condition_value,
                    condition_operator=section.condition_operator
                )
        
        serializer = self.get_serializer(new_template)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class InterventionReportViewSet(viewsets.ModelViewSet):
    """ViewSet for managing intervention reports"""
    queryset = InterventionReport.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReportCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ReportUpdateSerializer
        return InterventionReportSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by user permissions
        if not self.request.user.is_staff:
            queryset = queryset.filter(created_by=self.request.user)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit a report for review"""
        report = self.get_object()
        if report.status != 'draft':
            return Response(
                {'error': 'Only draft reports can be submitted'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        report.status = 'pending_review'
        report.submitted_at = timezone.now()
        report.save()
        
        # Create history entry
        ReportHistory.objects.create(
            report=report,
            action='status_changed',
            field_name='status',
            old_value='draft',
            new_value='pending_review',
            change_summary='Report submitted for review',
            user=request.user,
            ip_address=request.META.get('REMOTE_ADDR'),
            timestamp=timezone.now()
        )
        
        serializer = self.get_serializer(report)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a report"""
        report = self.get_object()
        if report.status != 'pending_review':
            return Response(
                {'error': 'Only pending reports can be approved'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        report.status = 'approved'
        report.approved_at = timezone.now()
        report.approved_by = request.user
        report.save()
        
        # Create history entry
        ReportHistory.objects.create(
            report=report,
            action='status_changed',
            field_name='status',
            old_value='pending_review',
            new_value='approved',
            change_summary='Report approved',
            user=request.user,
            ip_address=request.META.get('REMOTE_ADDR'),
            timestamp=timezone.now()
        )
        
        serializer = self.get_serializer(report)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a report"""
        report = self.get_object()
        if report.status != 'pending_review':
            return Response(
                {'error': 'Only pending reports can be rejected'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason', 'No reason provided')
        report.status = 'rejected'
        report.save()
        
        # Create history entry
        ReportHistory.objects.create(
            report=report,
            action='status_changed',
            field_name='status',
            old_value='pending_review',
            new_value='rejected',
            change_summary=f'Report rejected: {reason}',
            user=request.user,
            ip_address=request.META.get('REMOTE_ADDR'),
            timestamp=timezone.now()
        )
        
        serializer = self.get_serializer(report)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a report"""
        report = self.get_object()
        report.status = 'archived'
        report.save()
        
        # Create history entry
        ReportHistory.objects.create(
            report=report,
            action='status_changed',
            field_name='status',
            old_value=report.status,
            new_value='archived',
            change_summary='Report archived',
            user=request.user,
            ip_address=request.META.get('REMOTE_ADDR'),
            timestamp=timezone.now()
        )
        
        serializer = self.get_serializer(report)
        return Response(serializer.data)


class ReportSectionDataViewSet(viewsets.ModelViewSet):
    """ViewSet for managing report section data"""
    queryset = ReportSectionData.objects.all()
    serializer_class = ReportSectionDataSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        report_id = self.request.query_params.get('report_id')
        if report_id:
            queryset = queryset.filter(report_id=report_id)
        return queryset


class ReportMediaViewSet(viewsets.ModelViewSet):
    """ViewSet for managing report media"""
    queryset = ReportMedia.objects.all()
    serializer_class = ReportMediaSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        section_data_id = self.request.query_params.get('section_data_id')
        if section_data_id:
            queryset = queryset.filter(section_data_id=section_data_id)
        return queryset
    
    def perform_create(self, serializer):
        section_data_id = self.request.data.get('section_data_id')
        if not section_data_id:
            raise serializers.ValidationError("section_data_id is required")
        
        section_data = get_object_or_404(ReportSectionData, id=section_data_id)
        serializer.save(section_data=section_data)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download a media file"""
        media = self.get_object()
        if not media.file:
            raise Http404("File not found")
        
        response = HttpResponse(
            media.file.read(),
            content_type=media.mime_type
        )
        response['Content-Disposition'] = f'attachment; filename="{media.filename}"'
        return response
    
    @action(detail=True, methods=['get'])
    def thumbnail(self, request, pk=None):
        """Get thumbnail for media file"""
        media = self.get_object()
        if media.media_type != 'photo':
            raise Http404("Thumbnail not available for this media type")
        
        # For now, return the original image
        # In production, you'd generate and return a thumbnail
        if not media.file:
            raise Http404("File not found")
        
        response = HttpResponse(
            media.file.read(),
            content_type=media.mime_type
        )
        response['Content-Disposition'] = f'inline; filename="thumb_{media.filename}"'
        return response


class ReportSignatureViewSet(viewsets.ModelViewSet):
    """ViewSet for managing report signatures"""
    queryset = ReportSignature.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReportSignatureCreateSerializer
        return ReportSignatureSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        report_id = self.request.query_params.get('report_id')
        if report_id:
            queryset = queryset.filter(report_id=report_id)
        return queryset
    
    def perform_create(self, serializer):
        report_id = self.request.data.get('report_id')
        if not report_id:
            raise serializers.ValidationError("report_id is required")
        
        report = get_object_or_404(InterventionReport, id=report_id)
        serializer.save(report=report, context={'request': self.request})
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify a signature"""
        signature = self.get_object()
        # In production, implement proper signature verification
        signature.is_verified = True
        signature.save()
        
        serializer = self.get_serializer(signature)
        return Response(serializer.data)


class ReportExportViewSet(viewsets.ModelViewSet):
    """ViewSet for managing report exports"""
    queryset = ReportExport.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReportExportCreateSerializer
        return ReportExportSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        report_id = self.request.query_params.get('report_id')
        if report_id:
            queryset = queryset.filter(report_id=report_id)
        return queryset
    
    def perform_create(self, serializer):
        report_id = self.request.data.get('report_id')
        if not report_id:
            raise serializers.ValidationError("report_id is required")
        
        report = get_object_or_404(InterventionReport, id=report_id)
        serializer.save(report=report, user=self.request.user, context={'request': self.request})
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download an exported report"""
        export = self.get_object()
        if not os.path.exists(export.file_path):
            raise Http404("Export file not found")
        
        with open(export.file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{export.report.title}.{export.format}"'
            return response
    
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Share an export with a token"""
        export = self.get_object()
        days = request.data.get('days', 7)  # Default 7 days
        
        import secrets
        export.share_token = secrets.token_urlsafe(32)
        export.is_shared = True
        export.shared_at = timezone.now()
        export.expires_at = timezone.now() + timezone.timedelta(days=days)
        export.save()
        
        serializer = self.get_serializer(export)
        return Response(serializer.data)


class ReportHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing report history"""
    queryset = ReportHistory.objects.all()
    serializer_class = ReportHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        report_id = self.request.query_params.get('report_id')
        if report_id:
            queryset = queryset.filter(report_id=report_id)
        return queryset