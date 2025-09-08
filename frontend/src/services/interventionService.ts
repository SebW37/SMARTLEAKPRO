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

export interface Intervention {
  id: string;
  client_id: string;
  date_intervention: string;
  type_intervention: 'inspection' | 'détection' | 'réparation' | 'maintenance' | 'autre';
  statut: 'planifié' | 'en_cours' | 'validé' | 'archivé';
  lieu?: string;
  description?: string;
  technicien_assigné?: string;
  priorite: 'basse' | 'normale' | 'haute' | 'urgente';
  duree_estimee?: number;
  latitude?: string;
  longitude?: string;
  date_creation: string;
  date_modification?: string;
  date_debut?: string;
  date_fin?: string;
  client?: {
    id: string;
    nom: string;
    email?: string;
    telephone?: string;
  };
}

export interface InterventionCreate {
  client_id: string;
  date_intervention: string;
  type_intervention: 'inspection' | 'détection' | 'réparation' | 'maintenance' | 'autre';
  lieu?: string;
  description?: string;
  technicien_assigné?: string;
  priorite?: 'basse' | 'normale' | 'haute' | 'urgente';
  duree_estimee?: number;
  latitude?: string;
  longitude?: string;
}

export interface InterventionUpdate {
  date_intervention?: string;
  type_intervention?: 'inspection' | 'détection' | 'réparation' | 'maintenance' | 'autre';
  statut?: 'planifié' | 'en_cours' | 'validé' | 'archivé';
  lieu?: string;
  description?: string;
  technicien_assigné?: string;
  priorite?: 'basse' | 'normale' | 'haute' | 'urgente';
  duree_estimee?: number;
  latitude?: string;
  longitude?: string;
  date_debut?: string;
  date_fin?: string;
}

export interface InterventionListResponse {
  interventions: Intervention[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface StatutChange {
  nouveau_statut: 'planifié' | 'en_cours' | 'validé' | 'archivé';
  commentaire?: string;
  date_debut?: string;
  date_fin?: string;
}

export interface InterventionStats {
  par_statut: Record<string, number>;
  par_type: Record<string, number>;
  cette_semaine: number;
  total: number;
}

export const interventionService = {
  async getInterventions(
    page: number = 1, 
    size: number = 10, 
    client_id?: string,
    statut?: string,
    type_intervention?: string,
    priorite?: string,
    date_debut?: string,
    date_fin?: string,
    technicien?: string,
    search?: string
  ): Promise<InterventionListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
    });
    
    if (client_id) params.append('client_id', client_id);
    if (statut) params.append('statut', statut);
    if (type_intervention) params.append('type_intervention', type_intervention);
    if (priorite) params.append('priorite', priorite);
    if (date_debut) params.append('date_debut', date_debut);
    if (date_fin) params.append('date_fin', date_fin);
    if (technicien) params.append('technicien', technicien);
    if (search) params.append('search', search);
    
    const response = await api.get(`/interventions?${params.toString()}`);
    return response.data;
  },

  async getIntervention(id: string): Promise<Intervention> {
    const response = await api.get(`/interventions/${id}`);
    return response.data;
  },

  async createIntervention(interventionData: InterventionCreate): Promise<Intervention> {
    const response = await api.post('/interventions', interventionData);
    return response.data;
  },

  async updateIntervention(id: string, interventionData: InterventionUpdate): Promise<Intervention> {
    const response = await api.put(`/interventions/${id}`, interventionData);
    return response.data;
  },

  async deleteIntervention(id: string): Promise<void> {
    await api.delete(`/interventions/${id}`);
  },

  async changeStatus(id: string, statusChange: StatutChange): Promise<Intervention> {
    const response = await api.post(`/interventions/${id}/change-status`, statusChange);
    return response.data;
  },

  async getInterventionInspections(id: string): Promise<any[]> {
    const response = await api.get(`/interventions/${id}/inspections`);
    return response.data;
  },

  async getStats(): Promise<InterventionStats> {
    const response = await api.get('/interventions/stats/summary');
    return response.data;
  },
};
