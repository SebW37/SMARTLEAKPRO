from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    ReportTemplate, ReportSection, InterventionReport, 
    ReportSectionData, ReportMedia, ReportSignature, 
    ReportExport, ReportHistory
)


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'is_active', 'is_public', 'created_by', 'created_at']
    list_filter = ['template_type', 'is_active', 'is_public', 'created_at']
    search_fields = ['name', 'description', 'created_by__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    filter_horizontal = []
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'description', 'template_type')
        }),
        ('Settings', {
            'fields': ('is_active', 'is_public', 'created_by')
        }),
        ('Configuration', {
            'fields': ('configuration',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class ReportSectionInline(admin.TabularInline):
    model = ReportSection
    extra = 0
    fields = ['title', 'section_type', 'order', 'is_required', 'is_conditional']
    ordering = ['order']


@admin.register(ReportSection)
class ReportSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'template', 'section_type', 'order', 'is_required', 'is_conditional']
    list_filter = ['section_type', 'is_required', 'is_conditional', 'template']
    search_fields = ['title', 'template__name']
    ordering = ['template', 'order']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('template', 'title', 'section_type', 'order')
        }),
        ('Settings', {
            'fields': ('is_required', 'is_conditional')
        }),
        ('Conditional Logic', {
            'fields': ('condition_field', 'condition_value', 'condition_operator'),
            'classes': ('collapse',)
        }),
        ('Configuration', {
            'fields': ('configuration',),
            'classes': ('collapse',)
        }),
    )


class ReportSectionDataInline(admin.TabularInline):
    model = ReportSectionData
    extra = 0
    readonly_fields = ['section', 'created_at', 'updated_at']
    fields = ['section', 'value', 'created_at', 'updated_at']


class ReportMediaInline(admin.TabularInline):
    model = ReportMedia
    extra = 0
    readonly_fields = ['file_preview', 'file_size', 'created_at']
    fields = ['media_type', 'file', 'file_preview', 'title', 'file_size', 'created_at']
    
    def file_preview(self, obj):
        if obj.file and obj.media_type == 'photo':
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px;" />',
                obj.file.url
            )
        return "N/A"
    file_preview.short_description = "Preview"


class ReportSignatureInline(admin.TabularInline):
    model = ReportSignature
    extra = 0
    readonly_fields = ['signer', 'signature_type', 'signed_at', 'is_verified']
    fields = ['signer', 'signature_type', 'signed_at', 'is_verified']


@admin.register(InterventionReport)
class InterventionReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'intervention', 'template', 'status', 'version', 'created_by', 'created_at']
    list_filter = ['status', 'template', 'created_at', 'approved_at']
    search_fields = ['title', 'intervention__title', 'created_by__username']
    readonly_fields = ['id', 'created_at', 'updated_at', 'submitted_at', 'approved_at', 'last_exported']
    inlines = [ReportSectionDataInline, ReportMediaInline, ReportSignatureInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'intervention', 'template', 'title', 'status', 'version')
        }),
        ('Authors and Dates', {
            'fields': ('created_by', 'created_at', 'updated_at', 'submitted_at', 'approved_at', 'approved_by')
        }),
        ('Data', {
            'fields': ('data', 'export_formats', 'last_exported'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('intervention', 'template', 'created_by', 'approved_by')


@admin.register(ReportSectionData)
class ReportSectionDataAdmin(admin.ModelAdmin):
    list_display = ['report', 'section', 'value_preview', 'created_at']
    list_filter = ['section__section_type', 'created_at']
    search_fields = ['report__title', 'section__title', 'value']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def value_preview(self, obj):
        if len(obj.value) > 50:
            return obj.value[:50] + "..."
        return obj.value
    value_preview.short_description = "Value Preview"


@admin.register(ReportMedia)
class ReportMediaAdmin(admin.ModelAdmin):
    list_display = ['filename', 'media_type', 'title', 'file_size_display', 'created_at']
    list_filter = ['media_type', 'created_at']
    search_fields = ['filename', 'title', 'description']
    readonly_fields = ['id', 'file_size', 'created_at', 'updated_at']
    
    def file_size_display(self, obj):
        if obj.file_size:
            if obj.file_size < 1024:
                return f"{obj.file_size} B"
            elif obj.file_size < 1024 * 1024:
                return f"{obj.file_size / 1024:.1f} KB"
            else:
                return f"{obj.file_size / (1024 * 1024):.1f} MB"
        return "N/A"
    file_size_display.short_description = "File Size"


@admin.register(ReportSignature)
class ReportSignatureAdmin(admin.ModelAdmin):
    list_display = ['report', 'signer', 'signature_type', 'signed_at', 'is_verified']
    list_filter = ['signature_type', 'is_verified', 'signed_at']
    search_fields = ['report__title', 'signer__username']
    readonly_fields = ['id', 'signed_at', 'ip_address', 'user_agent', 'verification_hash']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('report', 'signer', 'signature_type')
        }),
        ('Signature Data', {
            'fields': ('signature_data', 'signature_image')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verification_hash')
        }),
        ('Metadata', {
            'fields': ('signed_at', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ReportExport)
class ReportExportAdmin(admin.ModelAdmin):
    list_display = ['report', 'format', 'file_size_display', 'exported_by', 'exported_at', 'is_shared']
    list_filter = ['format', 'is_shared', 'exported_at']
    search_fields = ['report__title', 'exported_by__username']
    readonly_fields = ['id', 'file_size', 'exported_at']
    
    def file_size_display(self, obj):
        if obj.file_size:
            if obj.file_size < 1024:
                return f"{obj.file_size} B"
            elif obj.file_size < 1024 * 1024:
                return f"{obj.file_size / 1024:.1f} KB"
            else:
                return f"{obj.file_size / (1024 * 1024):.1f} MB"
        return "N/A"
    file_size_display.short_description = "File Size"


@admin.register(ReportHistory)
class ReportHistoryAdmin(admin.ModelAdmin):
    list_display = ['report', 'action', 'user', 'timestamp', 'change_summary_preview']
    list_filter = ['action', 'timestamp', 'user']
    search_fields = ['report__title', 'user__username', 'change_summary']
    readonly_fields = ['id', 'timestamp', 'ip_address']
    
    def change_summary_preview(self, obj):
        if len(obj.change_summary) > 50:
            return obj.change_summary[:50] + "..."
        return obj.change_summary
    change_summary_preview.short_description = "Change Summary"
    
    def has_add_permission(self, request):
        return False  # History entries are created automatically