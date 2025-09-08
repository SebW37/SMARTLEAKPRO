from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    ReportTemplate, ReportSection, InterventionReport, 
    ReportSectionData, ReportMedia, ReportSignature, 
    ReportExport, ReportHistory
)


class ReportSectionSerializer(serializers.ModelSerializer):
    """Serializer for report sections"""
    
    class Meta:
        model = ReportSection
        fields = [
            'id', 'title', 'section_type', 'order', 'is_required', 
            'is_conditional', 'configuration', 'condition_field', 
            'condition_value', 'condition_operator', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReportTemplateSerializer(serializers.ModelSerializer):
    """Serializer for report templates"""
    sections = ReportSectionSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ReportTemplate
        fields = [
            'id', 'name', 'description', 'template_type', 'is_active', 
            'is_public', 'created_by', 'created_by_name', 'created_at', 
            'updated_at', 'configuration', 'sections'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReportMediaSerializer(serializers.ModelSerializer):
    """Serializer for report media"""
    file_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportMedia
        fields = [
            'id', 'media_type', 'file', 'file_url', 'thumbnail_url',
            'filename', 'file_size', 'mime_type', 'title', 'description',
            'annotation', 'latitude', 'longitude', 'altitude', 'captured_at',
            'width', 'height', 'duration', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'file_size', 'created_at', 'updated_at']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None
    
    def get_thumbnail_url(self, obj):
        if obj.media_type == 'photo' and obj.file:
            request = self.context.get('request')
            if request:
                # For now, return the same URL. In production, you'd generate thumbnails
                return request.build_absolute_uri(obj.file.url)
        return None


class ReportSectionDataSerializer(serializers.ModelSerializer):
    """Serializer for report section data"""
    media = ReportMediaSerializer(many=True, read_only=True)
    
    class Meta:
        model = ReportSectionData
        fields = [
            'id', 'section', 'value', 'data', 'media', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReportSignatureSerializer(serializers.ModelSerializer):
    """Serializer for report signatures"""
    signer_name = serializers.CharField(source='signer.get_full_name', read_only=True)
    signature_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportSignature
        fields = [
            'id', 'signer', 'signer_name', 'signature_type', 'signature_data',
            'signature_image', 'signature_image_url', 'signed_at', 'is_verified'
        ]
        read_only_fields = ['id', 'signed_at', 'is_verified']
    
    def get_signature_image_url(self, obj):
        if obj.signature_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.signature_image.url)
        return None


class ReportExportSerializerr(serializers.ModelSerializer):
    """Serializer for report exports"""
    exported_by_name = serializers.CharField(source='exported_by.get_full_name', read_only=True)
    download_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportExport
        fields = [
            'id', 'format', 'template_used', 'export_settings', 'file_path',
            'download_url', 'file_size', 'exported_by', 'exported_by_name',
            'exported_at', 'is_shared', 'shared_at', 'share_token', 'expires_at'
        ]
        read_only_fields = ['id', 'file_size', 'exported_at']
    
    def get_download_url(self, obj):
        if obj.file_path:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f'/api/reports/{obj.report.id}/exports/{obj.id}/download/')
        return None


class ReportHistorySerializer(serializers.ModelSerializer):
    """Serializer for report history"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = ReportHistory
        fields = [
            'id', 'action', 'field_name', 'old_value', 'new_value',
            'change_summary', 'user', 'user_name', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class InterventionReportSerializer(serializers.ModelSerializer):
    """Main serializer for intervention reports"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    section_data = ReportSectionDataSerializer(many=True, read_only=True)
    signatures = ReportSignatureSerializer(many=True, read_only=True)
    exports = ReportExportSerializerr(many=True, read_only=True)
    history = ReportHistorySerializer(many=True, read_only=True)
    
    class Meta:
        model = InterventionReport
        fields = [
            'id', 'intervention', 'template', 'template_name', 'title', 'status',
            'version', 'created_by', 'created_by_name', 'created_at', 'updated_at',
            'submitted_at', 'approved_at', 'approved_by', 'approved_by_name',
            'data', 'export_formats', 'last_exported', 'section_data', 'signatures',
            'exports', 'history'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'submitted_at', 'approved_at',
            'last_exported'
        ]


class ReportTemplateCreateSerializerr(serializers.ModelSerializer):
    """Serializer for creating report templates with sections"""
    sections = ReportSectionSerializer(many=True, required=False)
    
    class Meta:
        model = ReportTemplate
        fields = [
            'name', 'description', 'template_type', 'is_active', 'is_public',
            'configuration', 'sections'
        ]
    
    def create(self, validated_data):
        sections_data = validated_data.pop('sections', [])
        template = ReportTemplate.objects.create(**validated_data)
        
        for section_data in sections_data:
            ReportSection.objects.create(template=template, **section_data)
        
        return template


class ReportCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating intervention reports"""
    section_data = ReportSectionDataSerializer(many=True, required=False)
    
    class Meta:
        model = InterventionReport
        fields = [
            'intervention', 'template', 'title', 'data', 'section_data'
        ]
    
    def create(self, validated_data):
        section_data_list = validated_data.pop('section_data', [])
        report = InterventionReport.objects.create(**validated_data)
        
        # Create section data entries
        for section_data in section_data_list:
            ReportSectionData.objects.create(report=report, **section_data)
        
        return report


class ReportUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating intervention reports"""
    section_data = ReportSectionDataSerializer(many=True, required=False)
    
    class Meta:
        model = InterventionReport
        fields = [
            'title', 'status', 'data', 'section_data'
        ]
    
    def update(self, instance, validated_data):
        section_data_list = validated_data.pop('section_data', [])
        
        # Update report fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update section data
        if section_data_list:
            # Clear existing section data
            instance.section_data.all().delete()
            
            # Create new section data
            for section_data in section_data_list:
                ReportSectionData.objects.create(report=instance, **section_data)
        
        return instance


class ReportMediaUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading media to reports"""
    
    class Meta:
        model = ReportMedia
        fields = [
            'media_type', 'file', 'title', 'description', 'annotation',
            'latitude', 'longitude', 'altitude', 'captured_at'
        ]
    
    def create(self, validated_data):
        # Get the section_data from context
        section_data = self.context.get('section_data')
        if not section_data:
            raise serializers.ValidationError("Section data is required for media upload")
        
        # Calculate file size
        file = validated_data.get('file')
        if file:
            validated_data['file_size'] = file.size
            validated_data['filename'] = file.name
            validated_data['mime_type'] = file.content_type
        
        return ReportMedia.objects.create(section_data=section_data, **validated_data)


class ReportSignatureCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating report signatures"""
    
    class Meta:
        model = ReportSignature
        fields = [
            'signer', 'signature_type', 'signature_data', 'signature_image'
        ]
    
    def create(self, validated_data):
        # Get the report from context
        report = self.context.get('report')
        if not report:
            raise serializers.ValidationError("Report is required for signature")
        
        # Get request for IP and user agent
        request = self.context.get('request')
        if request:
            validated_data['ip_address'] = request.META.get('REMOTE_ADDR')
            validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        
        return ReportSignature.objects.create(report=report, **validated_data)


class ReportExportCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating report exports"""
    
    class Meta:
        model = ReportExport
        fields = [
            'format', 'template_used', 'export_settings'
        ]
    
    def create(self, validated_data):
        # Get the report from context
        report = self.context.get('report')
        if not report:
            raise serializers.ValidationError("Report is required for export")
        
        # Get the user from context
        user = self.context.get('user')
        if not user:
            raise serializers.ValidationError("User is required for export")
        
        validated_data['report'] = report
        validated_data['exported_by'] = user
        
        return ReportExport.objects.create(**validated_data)