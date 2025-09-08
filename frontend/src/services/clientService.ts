import { apiService } from './api';
import { Client, ClientSite, ApiResponse, ClientFilters } from '../types';

class ClientService {
  async getClients(filters?: ClientFilters, page = 1): Promise<ApiResponse<Client>> {
    const params = new URLSearchParams();
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== '') {
          params.append(key, value.toString());
        }
      });
    }
    
    params.append('page', page.toString());
    
    return apiService.get<ApiResponse<Client>>(`/clients/?${params.toString()}`);
  }

  async getClient(id: number): Promise<Client> {
    return apiService.get<Client>(`/clients/${id}/`);
  }

  async createClient(data: Partial<Client>): Promise<Client> {
    return apiService.post<Client>('/clients/', data);
  }

  async updateClient(id: number, data: Partial<Client>): Promise<Client> {
    return apiService.patch<Client>(`/clients/${id}/`, data);
  }

  async deleteClient(id: number): Promise<void> {
    return apiService.delete<void>(`/clients/${id}/`);
  }

  async getClientStats(): Promise<Record<string, any>> {
    return apiService.get<Record<string, any>>('/clients/stats/');
  }

  // Client Sites
  async getClientSites(clientId?: number, page = 1): Promise<ApiResponse<ClientSite>> {
    const params = new URLSearchParams();
    
    if (clientId) {
      params.append('client', clientId.toString());
    }
    
    params.append('page', page.toString());
    
    return apiService.get<ApiResponse<ClientSite>>(`/clients/sites/?${params.toString()}`);
  }

  async getClientSite(id: number): Promise<ClientSite> {
    return apiService.get<ClientSite>(`/clients/sites/${id}/`);
  }

  async createClientSite(data: Partial<ClientSite>): Promise<ClientSite> {
    return apiService.post<ClientSite>('/clients/sites/', data);
  }

  async updateClientSite(id: number, data: Partial<ClientSite>): Promise<ClientSite> {
    return apiService.patch<ClientSite>(`/clients/sites/${id}/`, data);
  }

  async deleteClientSite(id: number): Promise<void> {
    return apiService.delete<void>(`/clients/sites/${id}/`);
  }
}

export const clientService = new ClientService();
