"""
Serializers for intervention models.
"""
from rest_framework import serializers
from .models import Intervention, InterventionTask, InterventionDocument, InterventionNote


class InterventionTaskSerializer(serializers.ModelSerializer):
    """Serializer for InterventionTask model."""
    
    assigned_to_name = serializers.CharField(source='assigned_to.full_name', read_only=True)
    
    class Meta:
        model = InterventionTask
        fields = [
            'id', 'title', 'description', 'status', 'order', 'assigned_to',
            'assigned_to_name', 'estimated_duration', 'actual_duration',
            'started_at', 'completed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InterventionDocumentSerializer(serializers.ModelSerializer):
    """Serializer for InterventionDocument model."""
    
    uploaded_by_name = serializers.CharField(source='uploaded_by.full_name', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = InterventionDocument
        fields = [
            'id', 'intervention', 'task', 'title', 'document_type', 'file',
            'file_url', 'description', 'location', 'uploaded_by_name', 'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_at']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None


class InterventionNoteSerializer(serializers.ModelSerializer):
    """Serializer for InterventionNote model."""
    
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = InterventionNote
        fields = [
            'id', 'intervention', 'task', 'title', 'content', 'is_internal',
            'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InterventionSerializer(serializers.ModelSerializer):
    """Serializer for Intervention model."""
    
    client_name = serializers.CharField(source='client.name', read_only=True)
    site_name = serializers.CharField(source='site.name', read_only=True)
    assigned_technician_name = serializers.CharField(source='assigned_technician.full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    is_overdue = serializers.ReadOnlyField()
    duration = serializers.ReadOnlyField()
    
    class Meta:
        model = Intervention
        fields = [
            'id', 'title', 'description', 'intervention_type', 'status', 'priority',
            'client', 'site', 'client_name', 'site_name', 'scheduled_date',
            'estimated_duration', 'actual_start_date', 'actual_end_date',
            'assigned_technician', 'assigned_technician_name', 'created_by',
            'created_by_name', 'location', 'address', 'notes', 'materials_needed',
            'special_instructions', 'is_overdue', 'duration', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InterventionDetailSerializer(InterventionSerializer):
    """Detailed serializer for Intervention with related objects."""
    
    tasks = InterventionTaskSerializer(many=True, read_only=True)
    documents = InterventionDocumentSerializer(many=True, read_only=True)
    notes = InterventionNoteSerializer(many=True, read_only=True)
    
    class Meta(InterventionSerializer.Meta):
        fields = InterventionSerializer.Meta.fields + ['tasks', 'documents', 'notes']


class InterventionCalendarSerializer(serializers.ModelSerializer):
    """Serializer for calendar view of interventions."""
    
    client_name = serializers.CharField(source='client.name', read_only=True)
    site_name = serializers.CharField(source='site.name', read_only=True)
    assigned_technician_name = serializers.CharField(source='assigned_technician.full_name', read_only=True)
    
    class Meta:
        model = Intervention
        fields = [
            'id', 'title', 'scheduled_date', 'estimated_duration', 'status',
            'priority', 'client_name', 'site_name', 'assigned_technician_name',
            'intervention_type'
        ]
