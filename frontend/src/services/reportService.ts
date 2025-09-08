import { apiService } from './api';
import { Report, ApiResponse } from '../types';

class ReportService {
  async getReports(page = 1): Promise<ApiResponse<Report>> {
    const params = new URLSearchParams();
    params.append('page', page.toString());
    
    return apiService.get<ApiResponse<Report>>(`/reports/?${params.toString()}`);
  }

  async getReport(id: number): Promise<Report> {
    return apiService.get<Report>(`/reports/${id}/`);
  }

  async generateReport(data: {
    template: number;
    title: string;
    description?: string;
    format: 'pdf' | 'docx' | 'html' | 'xlsx';
    client?: number;
    intervention?: number;
    inspection?: number;
    content_config?: Record<string, any>;
  }): Promise<{ message: string; report_id: number }> {
    return apiService.post<{ message: string; report_id: number }>('/reports/generate/', data);
  }

  async downloadReport(id: number, filename?: string): Promise<void> {
    return apiService.downloadFile(`/reports/${id}/download/`, filename);
  }

  async viewReport(id: number): Promise<Report> {
    return apiService.get<Report>(`/reports/${id}/view/`);
  }

  async getReportStats(): Promise<Record<string, any>> {
    return apiService.get<Record<string, any>>('/reports/stats/');
  }
}

export const reportService = new ReportService();
