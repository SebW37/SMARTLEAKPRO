"""
Celery tasks for report generation.
"""
from celery import shared_task
from django.utils import timezone
from .models import Report
from .utils import generate_pdf_report, generate_docx_report, generate_html_report, generate_excel_report


@shared_task
def generate_report_task(report_id):
    """Generate a report asynchronously."""
    try:
        report = Report.objects.get(id=report_id)
        start_time = timezone.now()
        
        # Generate report based on format
        if report.format == 'pdf':
            file_path = generate_pdf_report(report)
        elif report.format == 'docx':
            file_path = generate_docx_report(report)
        elif report.format == 'html':
            file_path = generate_html_report(report)
        elif report.format == 'xlsx':
            file_path = generate_excel_report(report)
        else:
            raise ValueError(f"Unsupported format: {report.format}")
        
        # Update report with file
        with open(file_path, 'rb') as f:
            report.file.save(f"{report.title}.{report.format}", f, save=True)
        
        # Update report status
        end_time = timezone.now()
        report.status = 'completed'
        report.generated_at = end_time
        report.generation_duration = end_time - start_time
        report.file_size = report.file.size
        report.save()
        
        return f"Report {report_id} generated successfully"
        
    except Exception as e:
        # Update report status to failed
        try:
            report = Report.objects.get(id=report_id)
            report.status = 'failed'
            report.save()
        except Report.DoesNotExist:
            pass
        
        raise e
