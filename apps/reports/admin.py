from django.contrib import admin
from .models import ReportTemplate, ReportSection, InterventionReport, ReportSectionData, ReportMedia, ReportSignature, ReportExport, ReportHistory


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'is_active', 'created_at']
    list_filter = ['template_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']


@admin.register(ReportSection)
class ReportSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'section_type', 'order', 'is_required']
    list_filter = ['section_type', 'is_required', 'template']
    search_fields = ['title']


@admin.register(InterventionReport)
class InterventionReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title']


@admin.register(ReportSectionData)
class ReportSectionDataAdmin(admin.ModelAdmin):
    list_display = ['report', 'section', 'created_at']
    list_filter = ['created_at']


@admin.register(ReportMedia)
class ReportMediaAdmin(admin.ModelAdmin):
    list_display = ['filename', 'media_type', 'created_at']
    list_filter = ['media_type', 'created_at']


@admin.register(ReportSignature)
class ReportSignatureAdmin(admin.ModelAdmin):
    list_display = ['report', 'signer', 'signature_type', 'signed_at']
    list_filter = ['signature_type', 'signed_at']


@admin.register(ReportExport)
class ReportExportAdmin(admin.ModelAdmin):
    list_display = ['report', 'format', 'exported_at']
    list_filter = ['format', 'exported_at']


@admin.register(ReportHistory)
class ReportHistoryAdmin(admin.ModelAdmin):
    list_display = ['report', 'action', 'user', 'timestamp']
    list_filter = ['action', 'timestamp']
