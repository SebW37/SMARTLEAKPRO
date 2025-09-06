"""
Serializers for client models.
"""
from rest_framework import serializers
from .models import Client, ClientSite, ClientDocument, ClientNote


class ClientSerializer(serializers.ModelSerializer):
    """Serializer for Client model."""
    
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    sites_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = [
            'id', 'name', 'client_type', 'email', 'phone', 'address', 
            'city', 'postal_code', 'country', 'location', 'notes', 
            'is_active', 'created_by_name', 'sites_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_sites_count(self, obj):
        return obj.sites.count()


class ClientSiteSerializer(serializers.ModelSerializer):
    """Serializer for ClientSite model."""
    
    client_name = serializers.CharField(source='client.name', read_only=True)
    
    class Meta:
        model = ClientSite
        fields = [
            'id', 'client', 'client_name', 'name', 'description', 'address',
            'city', 'postal_code', 'country', 'location', 'contact_name',
            'contact_phone', 'contact_email', 'access_instructions', 'notes',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ClientDocumentSerializer(serializers.ModelSerializer):
    """Serializer for ClientDocument model."""
    
    client_name = serializers.CharField(source='client.name', read_only=True)
    site_name = serializers.CharField(source='site.name', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.full_name', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ClientDocument
        fields = [
            'id', 'client', 'site', 'client_name', 'site_name', 'title',
            'document_type', 'file', 'file_url', 'description', 'uploaded_by_name',
            'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_at']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None


class ClientNoteSerializer(serializers.ModelSerializer):
    """Serializer for ClientNote model."""
    
    client_name = serializers.CharField(source='client.name', read_only=True)
    site_name = serializers.CharField(source='site.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = ClientNote
        fields = [
            'id', 'client', 'site', 'client_name', 'site_name', 'title',
            'content', 'is_important', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ClientDetailSerializer(ClientSerializer):
    """Detailed serializer for Client with related objects."""
    
    sites = ClientSiteSerializer(many=True, read_only=True)
    documents = ClientDocumentSerializer(many=True, read_only=True)
    notes = ClientNoteSerializer(many=True, read_only=True)
    
    class Meta(ClientSerializer.Meta):
        fields = ClientSerializer.Meta.fields + ['sites', 'documents', 'notes']
