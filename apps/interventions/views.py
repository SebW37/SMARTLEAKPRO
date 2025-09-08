"""
Views for intervention management.
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Intervention, InterventionTask, InterventionDocument, InterventionNote
from .serializers import (
    InterventionSerializer, InterventionDetailSerializer, InterventionCalendarSerializer,
    InterventionTaskSerializer, InterventionDocumentSerializer, InterventionNoteSerializer
)


class InterventionListCreateView(generics.ListCreateAPIView):
    """List and create interventions."""
    
    queryset = Intervention.objects.all()
    serializer_class = InterventionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'priority', 'intervention_type', 'client', 'assigned_technician']
    search_fields = ['title', 'description', 'client__name', 'site__name']
    ordering_fields = ['scheduled_date', 'created_at', 'priority']
    ordering = ['-scheduled_date']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return InterventionSerializer
        return InterventionSerializer


class InterventionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an intervention."""
    
    queryset = Intervention.objects.all()
    serializer_class = InterventionDetailSerializer
    permission_classes = [permissions.IsAuthenticated]


class InterventionCalendarView(generics.ListAPIView):
    """Calendar view for interventions."""
    
    queryset = Intervention.objects.all()
    serializer_class = InterventionCalendarSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['assigned_technician', 'status', 'intervention_type']


class InterventionTaskListCreateView(generics.ListCreateAPIView):
    """List and create intervention tasks."""
    
    queryset = InterventionTask.objects.all()
    serializer_class = InterventionTaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['intervention', 'status', 'assigned_to']
    search_fields = ['title', 'description']
    ordering_fields = ['order', 'created_at']
    ordering = ['intervention', 'order']


class InterventionTaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an intervention task."""
    
    queryset = InterventionTask.objects.all()
    serializer_class = InterventionTaskSerializer
    permission_classes = [permissions.IsAuthenticated]


class InterventionDocumentListCreateView(generics.ListCreateAPIView):
    """List and create intervention documents."""
    
    queryset = InterventionDocument.objects.all()
    serializer_class = InterventionDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['intervention', 'task', 'document_type']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'uploaded_at']
    ordering = ['-uploaded_at']
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class InterventionDocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an intervention document."""
    
    queryset = InterventionDocument.objects.all()
    serializer_class = InterventionDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]


class InterventionNoteListCreateView(generics.ListCreateAPIView):
    """List and create intervention notes."""
    
    queryset = InterventionNote.objects.all()
    serializer_class = InterventionNoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['intervention', 'task', 'is_internal']
    search_fields = ['title', 'content']
    ordering_fields = ['title', 'created_at']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class InterventionNoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an intervention note."""
    
    queryset = InterventionNote.objects.all()
    serializer_class = InterventionNoteSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def intervention_stats_view(request):
    """Get intervention statistics."""
    now = timezone.now()
    
    stats = {
        'total_interventions': Intervention.objects.count(),
        'scheduled_interventions': Intervention.objects.filter(status='scheduled').count(),
        'in_progress_interventions': Intervention.objects.filter(status='in_progress').count(),
        'completed_interventions': Intervention.objects.filter(status='completed').count(),
        'overdue_interventions': Intervention.objects.filter(
            status__in=['scheduled', 'in_progress'],
            scheduled_date__lt=now
        ).count(),
        'today_interventions': Intervention.objects.filter(
            scheduled_date__date=now.date()
        ).count(),
        'this_week_interventions': Intervention.objects.filter(
            scheduled_date__date__gte=now.date() - timedelta(days=7),
            scheduled_date__date__lte=now.date()
        ).count(),
    }
    return Response(stats)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def start_intervention_view(request, pk):
    """Start an intervention."""
    try:
        intervention = Intervention.objects.get(pk=pk)
        if intervention.status != 'scheduled':
            return Response(
                {'error': 'Intervention must be scheduled to start'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        intervention.status = 'in_progress'
        intervention.actual_start_date = timezone.now()
        intervention.save()
        
        serializer = InterventionSerializer(intervention)
        return Response(serializer.data)
    except Intervention.DoesNotExist:
        return Response(
            {'error': 'Intervention not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def complete_intervention_view(request, pk):
    """Complete an intervention."""
    try:
        intervention = Intervention.objects.get(pk=pk)
        if intervention.status != 'in_progress':
            return Response(
                {'error': 'Intervention must be in progress to complete'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        intervention.status = 'completed'
        intervention.actual_end_date = timezone.now()
        intervention.save()
        
        serializer = InterventionSerializer(intervention)
        return Response(serializer.data)
    except Intervention.DoesNotExist:
        return Response(
            {'error': 'Intervention not found'},
            status=status.HTTP_404_NOT_FOUND
        )
