import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token aux requêtes
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface Client {
  id: string;
  nom: string;
  raison_sociale?: string;
  adresse?: string;
  telephone?: string;
  email?: string;
  statut: string;
  date_creation: string;
  date_modification?: string;
  notes?: string;
  contact_principal?: string;
}

export interface ClientCreate {
  nom: string;
  raison_sociale?: string;
  adresse?: string;
  telephone?: string;
  email?: string;
  notes?: string;
  contact_principal?: string;
}

export interface ClientUpdate {
  nom?: string;
  raison_sociale?: string;
  adresse?: string;
  telephone?: string;
  email?: string;
  statut?: string;
  notes?: string;
  contact_principal?: string;
}

export interface ClientListResponse {
  clients: Client[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export const clientService = {
  async getClients(page: number = 1, size: number = 10, search?: string, statut?: string): Promise<ClientListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
    });
    
    if (search) params.append('search', search);
    if (statut) params.append('statut', statut);
    
    const response = await api.get(`/clients?${params.toString()}`);
    return response.data;
  },

  async getClient(id: string): Promise<Client> {
    const response = await api.get(`/clients/${id}`);
    return response.data;
  },

  async createClient(clientData: ClientCreate): Promise<Client> {
    const response = await api.post('/clients', clientData);
    return response.data;
  },

  async updateClient(id: string, clientData: ClientUpdate): Promise<Client> {
    const response = await api.put(`/clients/${id}`, clientData);
    return response.data;
  },

  async deleteClient(id: string): Promise<void> {
    await api.delete(`/clients/${id}`);
  },
};
