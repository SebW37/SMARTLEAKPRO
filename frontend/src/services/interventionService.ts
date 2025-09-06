import { apiService } from './api';
import { Intervention, ApiResponse, InterventionFilters } from '../types';

class InterventionService {
  async getInterventions(filters?: InterventionFilters, page = 1): Promise<ApiResponse<Intervention>> {
    const params = new URLSearchParams();
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== '') {
          params.append(key, value.toString());
        }
      });
    }
    
    params.append('page', page.toString());
    
    return apiService.get<ApiResponse<Intervention>>(`/interventions/?${params.toString()}`);
  }

  async getIntervention(id: number): Promise<Intervention> {
    return apiService.get<Intervention>(`/interventions/${id}/`);
  }

  async createIntervention(data: Partial<Intervention>): Promise<Intervention> {
    return apiService.post<Intervention>('/interventions/', data);
  }

  async updateIntervention(id: number, data: Partial<Intervention>): Promise<Intervention> {
    return apiService.patch<Intervention>(`/interventions/${id}/`, data);
  }

  async deleteIntervention(id: number): Promise<void> {
    return apiService.delete<void>(`/interventions/${id}/`);
  }

  async getInterventionCalendar(filters?: { assigned_technician?: number; status?: string }): Promise<Intervention[]> {
    const params = new URLSearchParams();
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== '') {
          params.append(key, value.toString());
        }
      });
    }
    
    return apiService.get<Intervention[]>(`/interventions/calendar/?${params.toString()}`);
  }

  async getInterventionStats(): Promise<Record<string, any>> {
    return apiService.get<Record<string, any>>('/interventions/stats/');
  }

  async startIntervention(id: number): Promise<Intervention> {
    return apiService.post<Intervention>(`/interventions/${id}/start/`);
  }

  async completeIntervention(id: number): Promise<Intervention> {
    return apiService.post<Intervention>(`/interventions/${id}/complete/`);
  }
}

export const interventionService = new InterventionService();
