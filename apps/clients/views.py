"""
Views for client management.
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
# from django.contrib.gis.geos import Point
from .models import Client, ClientSite, ClientDocument
from .serializers import (
    ClientSerializer, ClientSiteSerializer, ClientDocumentSerializer
)


class ClientListCreateView(generics.ListCreateAPIView):
    """List and create clients."""
    
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['client_type', 'is_active', 'city']
    search_fields = ['name', 'email', 'phone', 'address', 'city']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ClientSerializer
        return ClientSerializer


class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a client."""
    
    queryset = Client.objects.all()
    serializer_class = ClientDetailSerializer
    permission_classes = [permissions.IsAuthenticated]


class ClientSiteListCreateView(generics.ListCreateAPIView):
    """List and create client sites."""
    
    queryset = ClientSite.objects.all()
    serializer_class = ClientSiteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['client', 'is_active', 'city']
    search_fields = ['name', 'description', 'address', 'city', 'contact_name']
    ordering_fields = ['name', 'created_at']
    ordering = ['client', 'name']


class ClientSiteDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a client site."""
    
    queryset = ClientSite.objects.all()
    serializer_class = ClientSiteSerializer
    permission_classes = [permissions.IsAuthenticated]


class ClientDocumentListCreateView(generics.ListCreateAPIView):
    """List and create client documents."""
    
    queryset = ClientDocument.objects.all()
    serializer_class = ClientDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['client', 'site', 'document_type']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'uploaded_at']
    ordering = ['-uploaded_at']
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class ClientDocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a client document."""
    
    queryset = ClientDocument.objects.all()
    serializer_class = ClientDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]


class ClientNoteListCreateView(generics.ListCreateAPIView):
    """List and create client notes."""
    
    queryset = ClientNote.objects.all()
    serializer_class = ClientNoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['client', 'site', 'is_important']
    search_fields = ['title', 'content']
    ordering_fields = ['title', 'created_at']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ClientNoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a client note."""
    
    queryset = ClientNote.objects.all()
    serializer_class = ClientNoteSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def client_stats_view(request):
    """Get client statistics."""
    stats = {
        'total_clients': Client.objects.count(),
        'active_clients': Client.objects.filter(is_active=True).count(),
        'total_sites': ClientSite.objects.count(),
        'active_sites': ClientSite.objects.filter(is_active=True).count(),
        'clients_by_type': dict(Client.objects.values_list('client_type').annotate(
            count=models.Count('id')
        )),
    }
    return Response(stats)
