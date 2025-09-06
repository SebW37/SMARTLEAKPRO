"""
Views for inspection management.
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from .models import (
    InspectionTemplate, Inspection, InspectionItem, 
    InspectionMedia, InspectionSignature
)
from .serializers import (
    InspectionTemplateSerializer, InspectionSerializer, InspectionDetailSerializer,
    InspectionFormSerializer, InspectionItemSerializer, InspectionMediaSerializer,
    InspectionSignatureSerializer
)


class InspectionTemplateListCreateView(generics.ListCreateAPIView):
    """List and create inspection templates."""
    
    queryset = InspectionTemplate.objects.all()
    serializer_class = InspectionTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class InspectionTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an inspection template."""
    
    queryset = InspectionTemplate.objects.all()
    serializer_class = InspectionTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]


class InspectionListCreateView(generics.ListCreateAPIView):
    """List and create inspections."""
    
    queryset = Inspection.objects.all()
    serializer_class = InspectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'client', 'site', 'inspector', 'template']
    search_fields = ['title', 'description', 'client__name', 'site__name']
    ordering_fields = ['inspection_date', 'created_at', 'score']
    ordering = ['-inspection_date']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return InspectionFormSerializer
        return InspectionSerializer


class InspectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an inspection."""
    
    queryset = Inspection.objects.all()
    serializer_class = InspectionDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return InspectionFormSerializer
        return InspectionDetailSerializer


class InspectionItemListCreateView(generics.ListCreateAPIView):
    """List and create inspection items."""
    
    queryset = InspectionItem.objects.all()
    serializer_class = InspectionItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['inspection', 'item_type', 'is_required']
    search_fields = ['label', 'value']
    ordering_fields = ['order', 'created_at']
    ordering = ['inspection', 'order']


class InspectionItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an inspection item."""
    
    queryset = InspectionItem.objects.all()
    serializer_class = InspectionItemSerializer
    permission_classes = [permissions.IsAuthenticated]


class InspectionMediaListCreateView(generics.ListCreateAPIView):
    """List and create inspection media."""
    
    queryset = InspectionMedia.objects.all()
    serializer_class = InspectionMediaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['inspection', 'item', 'media_type']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'uploaded_at', 'captured_at']
    ordering = ['-uploaded_at']
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class InspectionMediaDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete inspection media."""
    
    queryset = InspectionMedia.objects.all()
    serializer_class = InspectionMediaSerializer
    permission_classes = [permissions.IsAuthenticated]


class InspectionSignatureListCreateView(generics.ListCreateAPIView):
    """List and create inspection signatures."""
    
    queryset = InspectionSignature.objects.all()
    serializer_class = InspectionSignatureSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['inspection', 'item']
    search_fields = ['signer_name', 'signer_role']
    ordering_fields = ['signed_at', 'created_at']
    ordering = ['-signed_at']


class InspectionSignatureDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete inspection signatures."""
    
    queryset = InspectionSignature.objects.all()
    serializer_class = InspectionSignatureSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def start_inspection_view(request, pk):
    """Start an inspection."""
    try:
        inspection = Inspection.objects.get(pk=pk)
        if inspection.status != 'draft':
            return Response(
                {'error': 'Inspection must be in draft status to start'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        inspection.status = 'in_progress'
        inspection.started_at = timezone.now()
        inspection.inspector = request.user
        inspection.save()
        
        serializer = InspectionSerializer(inspection)
        return Response(serializer.data)
    except Inspection.DoesNotExist:
        return Response(
            {'error': 'Inspection not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def complete_inspection_view(request, pk):
    """Complete an inspection."""
    try:
        inspection = Inspection.objects.get(pk=pk)
        if inspection.status != 'in_progress':
            return Response(
                {'error': 'Inspection must be in progress to complete'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        inspection.status = 'completed'
        inspection.completed_at = timezone.now()
        inspection.save()
        
        serializer = InspectionSerializer(inspection)
        return Response(serializer.data)
    except Inspection.DoesNotExist:
        return Response(
            {'error': 'Inspection not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def validate_inspection_view(request, pk):
    """Validate an inspection."""
    try:
        inspection = Inspection.objects.get(pk=pk)
        if inspection.status != 'completed':
            return Response(
                {'error': 'Inspection must be completed to validate'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        inspection.status = 'validated'
        inspection.save()
        
        serializer = InspectionSerializer(inspection)
        return Response(serializer.data)
    except Inspection.DoesNotExist:
        return Response(
            {'error': 'Inspection not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def inspection_stats_view(request):
    """Get inspection statistics."""
    stats = {
        'total_inspections': Inspection.objects.count(),
        'draft_inspections': Inspection.objects.filter(status='draft').count(),
        'in_progress_inspections': Inspection.objects.filter(status='in_progress').count(),
        'completed_inspections': Inspection.objects.filter(status='completed').count(),
        'validated_inspections': Inspection.objects.filter(status='validated').count(),
        'today_inspections': Inspection.objects.filter(
            inspection_date__date=timezone.now().date()
        ).count(),
        'this_week_inspections': Inspection.objects.filter(
            inspection_date__date__gte=timezone.now().date() - timezone.timedelta(days=7),
            inspection_date__date__lte=timezone.now().date()
        ).count(),
    }
    return Response(stats)
