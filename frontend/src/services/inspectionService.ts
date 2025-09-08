import { apiService } from './api';
import { Inspection, InspectionItem, ApiResponse, InspectionFilters } from '../types';

class InspectionService {
  async getInspections(filters?: InspectionFilters, page = 1): Promise<ApiResponse<Inspection>> {
    const params = new URLSearchParams();
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== '') {
          params.append(key, value.toString());
        }
      });
    }
    
    params.append('page', page.toString());
    
    return apiService.get<ApiResponse<Inspection>>(`/inspections/?${params.toString()}`);
  }

  async getInspection(id: number): Promise<Inspection> {
    return apiService.get<Inspection>(`/inspections/${id}/`);
  }

  async createInspection(data: Partial<Inspection>): Promise<Inspection> {
    return apiService.post<Inspection>('/inspections/', data);
  }

  async updateInspection(id: number, data: Partial<Inspection>): Promise<Inspection> {
    return apiService.patch<Inspection>(`/inspections/${id}/`, data);
  }

  async deleteInspection(id: number): Promise<void> {
    return apiService.delete<void>(`/inspections/${id}/`);
  }

  async getInspectionStats(): Promise<Record<string, any>> {
    return apiService.get<Record<string, any>>('/inspections/stats/');
  }

  async startInspection(id: number): Promise<Inspection> {
    return apiService.post<Inspection>(`/inspections/${id}/start/`);
  }

  async completeInspection(id: number): Promise<Inspection> {
    return apiService.post<Inspection>(`/inspections/${id}/complete/`);
  }

  async validateInspection(id: number): Promise<Inspection> {
    return apiService.post<Inspection>(`/inspections/${id}/validate/`);
  }

  // Inspection Items
  async getInspectionItems(inspectionId?: number, page = 1): Promise<ApiResponse<InspectionItem>> {
    const params = new URLSearchParams();
    
    if (inspectionId) {
      params.append('inspection', inspectionId.toString());
    }
    
    params.append('page', page.toString());
    
    return apiService.get<ApiResponse<InspectionItem>>(`/inspections/items/?${params.toString()}`);
  }

  async getInspectionItem(id: number): Promise<InspectionItem> {
    return apiService.get<InspectionItem>(`/inspections/items/${id}/`);
  }

  async createInspectionItem(data: Partial<InspectionItem>): Promise<InspectionItem> {
    return apiService.post<InspectionItem>('/inspections/items/', data);
  }

  async updateInspectionItem(id: number, data: Partial<InspectionItem>): Promise<InspectionItem> {
    return apiService.patch<InspectionItem>(`/inspections/items/${id}/`, data);
  }

  async deleteInspectionItem(id: number): Promise<void> {
    return apiService.delete<void>(`/inspections/items/${id}/`);
  }
}

export const inspectionService = new InspectionService();
