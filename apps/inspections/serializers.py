"""
Serializers for inspection models.
"""
from rest_framework import serializers
from .models import (
    InspectionTemplate, Inspection, InspectionItem, 
    InspectionMedia, InspectionSignature
)


class InspectionTemplateSerializer(serializers.ModelSerializer):
    """Serializer for InspectionTemplate model."""
    
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = InspectionTemplate
        fields = [
            'id', 'name', 'description', 'category', 'is_active',
            'form_config', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InspectionItemSerializer(serializers.ModelSerializer):
    """Serializer for InspectionItem model."""
    
    class Meta:
        model = InspectionItem
        fields = [
            'id', 'template_item_id', 'label', 'item_type', 'value',
            'is_required', 'order', 'show_condition', 'location',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InspectionMediaSerializer(serializers.ModelSerializer):
    """Serializer for InspectionMedia model."""
    
    uploaded_by_name = serializers.CharField(source='uploaded_by.full_name', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = InspectionMedia
        fields = [
            'id', 'inspection', 'item', 'title', 'media_type', 'file',
            'file_url', 'description', 'location', 'captured_at',
            'uploaded_by_name', 'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_at']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None


class InspectionSignatureSerializer(serializers.ModelSerializer):
    """Serializer for InspectionSignature model."""
    
    class Meta:
        model = InspectionSignature
        fields = [
            'id', 'inspection', 'item', 'signer_name', 'signer_role',
            'signature_data', 'location', 'signed_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class InspectionSerializer(serializers.ModelSerializer):
    """Serializer for Inspection model."""
    
    client_name = serializers.CharField(source='client.name', read_only=True)
    site_name = serializers.CharField(source='site.name', read_only=True)
    inspector_name = serializers.CharField(source='inspector.full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    duration = serializers.ReadOnlyField()
    score_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = Inspection
        fields = [
            'id', 'title', 'description', 'status', 'template', 'form_data',
            'client', 'site', 'client_name', 'site_name', 'intervention',
            'location', 'address', 'inspection_date', 'started_at', 'completed_at',
            'inspector', 'inspector_name', 'created_by', 'created_by_name',
            'score', 'max_score', 'compliance_status', 'score_percentage',
            'notes', 'recommendations', 'duration', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InspectionDetailSerializer(InspectionSerializer):
    """Detailed serializer for Inspection with related objects."""
    
    items = InspectionItemSerializer(many=True, read_only=True)
    media = InspectionMediaSerializer(many=True, read_only=True)
    signatures = InspectionSignatureSerializer(many=True, read_only=True)
    
    class Meta(InspectionSerializer.Meta):
        fields = InspectionSerializer.Meta.fields + ['items', 'media', 'signatures']


class InspectionFormSerializer(serializers.ModelSerializer):
    """Serializer for inspection form data."""
    
    items = InspectionItemSerializer(many=True, required=False)
    
    class Meta:
        model = Inspection
        fields = [
            'id', 'title', 'description', 'template', 'form_data',
            'client', 'site', 'intervention', 'location', 'address',
            'inspection_date', 'inspector', 'notes', 'recommendations',
            'items'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        inspection = Inspection.objects.create(**validated_data)
        
        for item_data in items_data:
            InspectionItem.objects.create(inspection=inspection, **item_data)
        
        return inspection
    
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', [])
        
        # Update inspection
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update items
        if items_data:
            # Clear existing items
            instance.items.all().delete()
            
            # Create new items
            for item_data in items_data:
                InspectionItem.objects.create(inspection=instance, **item_data)
        
        return instance
