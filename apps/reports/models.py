from django.db import models
from django.contrib.auth.models import User
from django.db.models import JSONField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


class ReportTemplate(models.Model):
    """Template for intervention reports with customizable structure"""
    
    TEMPLATE_TYPES = [
        ('standard', 'Standard'),
        ('emergency', 'Emergency'),
        ('maintenance', 'Maintenance'),
        ('inspection', 'Inspection'),
        ('custom', 'Custom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Template Name")
    description = models.TextField(blank=True, verbose_name="Description")
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES, default='standard')
    is_active = models.BooleanField(default=True, verbose_name="Active")
    is_public = models.BooleanField(default=False, verbose_name="Public Template")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Template configuration as JSON
    configuration = models.JSONField(default=dict, verbose_name="Template Configuration")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Report Template"
        verbose_name_plural = "Report Templates"
    
    def __str__(self):
        return self.name


class ReportSection(models.Model):
    """Dynamic sections within a report template"""
    
    SECTION_TYPES = [
        ('text', 'Text Field'),
        ('textarea', 'Long Text'),
        ('checklist', 'Checklist'),
        ('radio', 'Radio Buttons'),
        ('select', 'Dropdown'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('datetime', 'Date & Time'),
        ('photo', 'Photo'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('sketch', 'Sketch/Drawing'),
        ('signature', 'Digital Signature'),
        ('score', 'Score/Rating'),
        ('calculation', 'Calculation'),
        ('location', 'GPS Location'),
        ('file', 'File Upload'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=200, verbose_name="Section Title")
    section_type = models.CharField(max_length=20, choices=SECTION_TYPES)
    order = models.PositiveIntegerField(default=0, verbose_name="Display Order")
    is_required = models.BooleanField(default=False, verbose_name="Required")
    is_conditional = models.BooleanField(default=False, verbose_name="Conditional Field")
    
    # Configuration for the section
    configuration = models.JSONField(default=dict, verbose_name="Section Configuration")
    
    # Conditional logic
    condition_field = models.CharField(max_length=100, blank=True, verbose_name="Condition Field")
    condition_value = models.CharField(max_length=200, blank=True, verbose_name="Condition Value")
    condition_operator = models.CharField(max_length=10, default='equals', verbose_name="Condition Operator")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "Report Section"
        verbose_name_plural = "Report Sections"
    
    def __str__(self):
        return f"{self.template.name} - {self.title}"


class InterventionReport(models.Model):
    """Main intervention report instance"""
    
    REPORT_STATUS = [
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('pending_review', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    intervention = models.ForeignKey('interventions.Intervention', on_delete=models.CASCADE, related_name='reports')
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='reports')
    
    # Report metadata
    title = models.CharField(max_length=300, verbose_name="Report Title")
    status = models.CharField(max_length=20, choices=REPORT_STATUS, default='draft')
    version = models.PositiveIntegerField(default=1, verbose_name="Version")
    
    # Authors and dates
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_reports')
    
    # Report data
    data = models.JSONField(default=dict, verbose_name="Report Data")
    
    # Export settings
    export_formats = models.JSONField(default=list, verbose_name="Available Export Formats")
    last_exported = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Intervention Report"
        verbose_name_plural = "Intervention Reports"
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"


class ReportSectionData(models.Model):
    """Data for each section of a report"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(InterventionReport, on_delete=models.CASCADE, related_name='section_data')
    section = models.ForeignKey(ReportSection, on_delete=models.CASCADE, related_name='data_instances')
    
    # Section data
    value = models.TextField(blank=True, verbose_name="Section Value")
    data = models.JSONField(default=dict, verbose_name="Section Data")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['report', 'section']
        verbose_name = "Report Section Data"
        verbose_name_plural = "Report Section Data"
    
    def __str__(self):
        return f"{self.report.title} - {self.section.title}"


class ReportMedia(models.Model):
    """Media files attached to report sections"""
    
    MEDIA_TYPES = [
        ('photo', 'Photo'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('sketch', 'Sketch'),
        ('file', 'File'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section_data = models.ForeignKey(ReportSectionData, on_delete=models.CASCADE, related_name='media')
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES)
    
    # File information
    file = models.FileField(upload_to='reports/media/%Y/%m/%d/', verbose_name="Media File")
    filename = models.CharField(max_length=255, verbose_name="Original Filename")
    file_size = models.PositiveIntegerField(verbose_name="File Size (bytes)")
    mime_type = models.CharField(max_length=100, verbose_name="MIME Type")
    
    # Metadata
    title = models.CharField(max_length=200, blank=True, verbose_name="Media Title")
    description = models.TextField(blank=True, verbose_name="Description")
    annotation = models.TextField(blank=True, verbose_name="Annotation")
    
    # Location and timing
    latitude = models.FloatField(null=True, blank=True, verbose_name="Latitude")
    longitude = models.FloatField(null=True, blank=True, verbose_name="Longitude")
    altitude = models.FloatField(null=True, blank=True, verbose_name="Altitude")
    captured_at = models.DateTimeField(null=True, blank=True, verbose_name="Captured At")
    
    # Technical metadata
    width = models.PositiveIntegerField(null=True, blank=True, verbose_name="Width")
    height = models.PositiveIntegerField(null=True, blank=True, verbose_name="Height")
    duration = models.DurationField(null=True, blank=True, verbose_name="Duration")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Report Media"
        verbose_name_plural = "Report Media"
    
    def __str__(self):
        return f"{self.get_media_type_display()} - {self.title or self.filename}"


class ReportSignature(models.Model):
    """Digital signatures for reports"""
    
    SIGNATURE_TYPES = [
        ('author', 'Author Signature'),
        ('reviewer', 'Reviewer Signature'),
        ('client', 'Client Signature'),
        ('approver', 'Approver Signature'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(InterventionReport, on_delete=models.CASCADE, related_name='signatures')
    signer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_signatures')
    signature_type = models.CharField(max_length=20, choices=SIGNATURE_TYPES)
    
    # Signature data
    signature_data = models.TextField(verbose_name="Signature Data (Base64)")
    signature_image = models.ImageField(upload_to='reports/signatures/%Y/%m/%d/', null=True, blank=True)
    
    # Metadata
    signed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(verbose_name="IP Address")
    user_agent = models.TextField(verbose_name="User Agent")
    
    # Verification
    is_verified = models.BooleanField(default=False, verbose_name="Verified")
    verification_hash = models.CharField(max_length=64, blank=True, verbose_name="Verification Hash")
    
    class Meta:
        ordering = ['-signed_at']
        verbose_name = "Report Signature"
        verbose_name_plural = "Report Signatures"
    
    def __str__(self):
        return f"{self.report.title} - {self.get_signature_type_display()} by {self.signer.get_full_name()}"


class ReportExport(models.Model):
    """Export history and settings for reports"""
    
    EXPORT_FORMATS = [
        ('pdf', 'PDF'),
        ('docx', 'Word Document'),
        ('html', 'HTML'),
        ('json', 'JSON'),
        ('xml', 'XML'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(InterventionReport, on_delete=models.CASCADE, related_name='exports')
    format = models.CharField(max_length=10, choices=EXPORT_FORMATS)
    
    # Export settings
    template_used = models.CharField(max_length=200, blank=True, verbose_name="Template Used")
    export_settings = models.JSONField(default=dict, verbose_name="Export Settings")
    
    # File information
    file_path = models.CharField(max_length=500, verbose_name="File Path")
    file_size = models.PositiveIntegerField(verbose_name="File Size (bytes)")
    
    # Metadata
    exported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_exports')
    exported_at = models.DateTimeField(auto_now_add=True)
    
    # Sharing
    is_shared = models.BooleanField(default=False, verbose_name="Shared")
    shared_at = models.DateTimeField(null=True, blank=True)
    share_token = models.CharField(max_length=64, blank=True, verbose_name="Share Token")
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-exported_at']
        verbose_name = "Report Export"
        verbose_name_plural = "Report Exports"
    
    def __str__(self):
        return f"{self.report.title} - {self.get_format_display()}"


class ReportHistory(models.Model):
    """Version history and audit trail for reports"""
    
    ACTION_TYPES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('section_added', 'Section Added'),
        ('section_modified', 'Section Modified'),
        ('section_deleted', 'Section Deleted'),
        ('media_added', 'Media Added'),
        ('media_removed', 'Media Removed'),
        ('status_changed', 'Status Changed'),
        ('signed', 'Signed'),
        ('exported', 'Exported'),
        ('shared', 'Shared'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(InterventionReport, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    
    # Change details
    field_name = models.CharField(max_length=100, blank=True, verbose_name="Field Name")
    old_value = models.TextField(blank=True, verbose_name="Old Value")
    new_value = models.TextField(blank=True, verbose_name="New Value")
    change_summary = models.TextField(blank=True, verbose_name="Change Summary")
    
    # Metadata
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_changes')
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(verbose_name="IP Address")
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Report History"
        verbose_name_plural = "Report History"
    
    def __str__(self):
        return f"{self.report.title} - {self.get_action_display()} by {self.user.get_full_name()}"