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

export interface RendezVous {
  id: string;
  client_id: string;
  intervention_id?: string;
  date_heure_debut: string;
  date_heure_fin: string;
  statut: 'planifié' | 'confirmé' | 'annulé' | 'terminé';
  utilisateur_responsable?: string;
  notes?: string;
  couleur?: string;
  rappel_avant: number;
  date_creation: string;
  date_modification?: string;
  client?: {
    id: string;
    nom: string;
    email?: string;
    telephone?: string;
  };
  intervention?: {
    id: string;
    type_intervention: string;
    description?: string;
  };
}

export interface RendezVousCreate {
  client_id: string;
  intervention_id?: string;
  date_heure_debut: string;
  date_heure_fin: string;
  utilisateur_responsable?: string;
  notes?: string;
  couleur?: string;
  rappel_avant?: number;
}

export interface RendezVousUpdate {
  date_heure_debut?: string;
  date_heure_fin?: string;
  statut?: 'planifié' | 'confirmé' | 'annulé' | 'terminé';
  utilisateur_responsable?: string;
  notes?: string;
  couleur?: string;
  rappel_avant?: number;
}

export interface RendezVousListResponse {
  rendez_vous: RendezVous[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface CalendarEvent {
  id: string;
  title: string;
  start: string;
  end: string;
  backgroundColor: string;
  borderColor: string;
  textColor: string;
  extendedProps: {
    statut: string;
    client: string;
    intervention?: string;
    technicien?: string;
    notes?: string;
    rappel_avant: number;
  };
}

export interface RendezVousCalendarResponse {
  events: CalendarEvent[];
  total: number;
}

export interface PlanningStats {
  total_rdv: number;
  rdv_aujourd_hui: number;
  rdv_cette_semaine: number;
  rdv_en_retard: number;
  par_statut: Record<string, number>;
  par_technicien: Record<string, number>;
}

export interface ValidationCreneau {
  technicien?: string;
  date_debut: string;
  date_fin: string;
  rdv_id_exclu?: string;
}

export const planningService = {
  async getRendezVous(
    page: number = 1,
    size: number = 10,
    client_id?: string,
    statut?: string,
    technicien?: string,
    date_debut?: string,
    date_fin?: string
  ): Promise<RendezVousListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
    });
    
    if (client_id) params.append('client_id', client_id);
    if (statut) params.append('statut', statut);
    if (technicien) params.append('technicien', technicien);
    if (date_debut) params.append('date_debut', date_debut);
    if (date_fin) params.append('date_fin', date_fin);
    
    const response = await api.get(`/planning?${params.toString()}`);
    return response.data;
  },

  async getCalendarEvents(
    start?: string,
    end?: string,
    technicien?: string
  ): Promise<RendezVousCalendarResponse> {
    const params = new URLSearchParams();
    
    if (start) params.append('start', start);
    if (end) params.append('end', end);
    if (technicien) params.append('technicien', technicien);
    
    const response = await api.get(`/planning/calendar?${params.toString()}`);
    return response.data;
  },

  async getRendezVous(id: string): Promise<RendezVous> {
    const response = await api.get(`/planning/${id}`);
    return response.data;
  },

  async createRendezVous(rdvData: RendezVousCreate): Promise<RendezVous> {
    const response = await api.post('/planning', rdvData);
    return response.data;
  },

  async updateRendezVous(id: string, rdvData: RendezVousUpdate): Promise<RendezVous> {
    const response = await api.put(`/planning/${id}`, rdvData);
    return response.data;
  },

  async deleteRendezVous(id: string): Promise<void> {
    await api.delete(`/planning/${id}`);
  },

  async validateCreneau(validationData: ValidationCreneau): Promise<{valid: boolean, message: string}> {
    const response = await api.post('/planning/validate-creneau', validationData);
    return response.data;
  },

  async getStats(): Promise<PlanningStats> {
    const response = await api.get('/planning/stats/planning');
    return response.data;
  },
};
