from rest_framework import serializers
from .models import (
    Client, ClientSite, ClientContact, ClientContract, 
    ClientDocument, ClientNotification, ClientActivityLog
)


class ClientSerializer(serializers.ModelSerializer):
    """Basic client serializer."""
    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ('client_number', 'created_at', 'updated_at')


class ClientDetailSerializer(serializers.ModelSerializer):
    """Detailed client serializer with related data."""
    contacts = serializers.StringRelatedField(many=True, read_only=True)
    contracts = serializers.StringRelatedField(many=True, read_only=True)
    sites = serializers.StringRelatedField(many=True, read_only=True)
    documents_count = serializers.SerializerMethodField()
    notifications_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ('client_number', 'created_at', 'updated_at')
    
    def get_documents_count(self, obj):
        return obj.documents.count()
    
    def get_notifications_count(self, obj):
        return obj.notifications.count()


class ClientSiteSerializer(serializers.ModelSerializer):
    """Client site serializer."""
    class Meta:
        model = ClientSite
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ClientContactSerializer(serializers.ModelSerializer):
    """Client contact serializer."""
    class Meta:
        model = ClientContact
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ClientContractSerializer(serializers.ModelSerializer):
    """Client contract serializer."""
    class Meta:
        model = ClientContract
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ClientDocumentSerializer(serializers.ModelSerializer):
    """Client document serializer."""
    class Meta:
        model = ClientDocument
        fields = '__all__'
        read_only_fields = ('uploaded_at',)


class ClientNotificationSerializer(serializers.ModelSerializer):
    """Client notification serializer."""
    class Meta:
        model = ClientNotification
        fields = '__all__'
        read_only_fields = ('created_at',)


class ClientActivityLogSerializer(serializers.ModelSerializer):
    """Client activity log serializer."""
    class Meta:
        model = ClientActivityLog
        fields = '__all__'
        read_only_fields = ('created_at',)

