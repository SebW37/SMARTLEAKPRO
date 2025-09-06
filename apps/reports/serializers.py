"""
Serializers for report models.
"""
from rest_framework import serializers
from .models import ReportTemplate, Report, ReportSchedule, ReportAnalytics


class ReportTemplateSerializer(serializers.ModelSerializer):
    """Serializer for ReportTemplate model."""
    
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = ReportTemplate
        fields = [
            'id', 'name', 'description', 'template_type', 'is_active',
            'template_config', 'html_template', 'css_styles', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReportSerializer(serializers.ModelSerializer):
    """Serializer for Report model."""
    
    client_name = serializers.CharField(source='client.name', read_only=True)
    intervention_title = serializers.CharField(source='intervention.title', read_only=True)
    inspection_title = serializers.CharField(source='inspection.title', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = [
            'id', 'title', 'description', 'status', 'format', 'template',
            'content', 'client', 'client_name', 'intervention', 'intervention_title',
            'inspection', 'inspection_title', 'file', 'file_url', 'file_size',
            'generated_at', 'generation_duration', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None


class ReportScheduleSerializer(serializers.ModelSerializer):
    """Serializer for ReportSchedule model."""
    
    template_name = serializers.CharField(source='template.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = ReportSchedule
        fields = [
            'id', 'name', 'description', 'is_active', 'template', 'template_name',
            'frequency', 'schedule_config', 'email_recipients', 'created_by_name',
            'created_at', 'updated_at', 'last_run', 'next_run'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_run', 'next_run']


class ReportAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for ReportAnalytics model."""
    
    report_title = serializers.CharField(source='report.title', read_only=True)
    viewed_by_names = serializers.StringRelatedField(source='viewed_by', many=True, read_only=True)
    downloaded_by_names = serializers.StringRelatedField(source='downloaded_by', many=True, read_only=True)
    
    class Meta:
        model = ReportAnalytics
        fields = [
            'id', 'report', 'report_title', 'view_count', 'download_count',
            'viewed_by_names', 'downloaded_by_names', 'first_viewed_at',
            'last_viewed_at', 'first_downloaded_at', 'last_downloaded_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReportGenerationSerializer(serializers.Serializer):
    """Serializer for report generation requests."""
    
    template = serializers.PrimaryKeyRelatedField(queryset=ReportTemplate.objects.filter(is_active=True))
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    format = serializers.ChoiceField(choices=Report.FORMAT_CHOICES, default='pdf')
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(), required=False)
    intervention = serializers.PrimaryKeyRelatedField(queryset=Intervention.objects.all(), required=False)
    inspection = serializers.PrimaryKeyRelatedField(queryset=Inspection.objects.all(), required=False)
    content_config = serializers.JSONField(required=False, default=dict)
    
    def validate(self, attrs):
        # Ensure at least one related object is provided
        if not any([attrs.get('client'), attrs.get('intervention'), attrs.get('inspection')]):
            raise serializers.ValidationError(
                "At least one related object (client, intervention, or inspection) must be provided."
            )
        return attrs
