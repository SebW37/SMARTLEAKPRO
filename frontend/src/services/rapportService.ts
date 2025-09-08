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

export interface Rapport {
  id: string;
  intervention_id: string;
  date_creation: string;
  type_rapport: 'inspection' | 'validation' | 'intervention' | 'maintenance' | 'autre';
  contenu?: any;
  auteur_rapport?: string;
  statut: 'brouillon' | 'validé' | 'archivé';
  titre: string;
  description?: string;
  taille_fichier?: number;
  type_fichier?: string;
  version: string;
  chemin_fichier?: string;
  date_modification?: string;
  date_validation?: string;
  date_archivage?: string;
  intervention?: {
    id: string;
    type_intervention: string;
    client?: {
      nom: string;
      email?: string;
    };
  };
}

export interface RapportCreate {
  intervention_id: string;
  type_rapport: 'inspection' | 'validation' | 'intervention' | 'maintenance' | 'autre';
  titre: string;
  description?: string;
  auteur_rapport?: string;
  contenu?: any;
}

export interface RapportUpdate {
  titre?: string;
  description?: string;
  statut?: 'brouillon' | 'validé' | 'archivé';
  contenu?: any;
  auteur_rapport?: string;
}

export interface RapportListResponse {
  rapports: Rapport[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface GenerationRapport {
  intervention_id: string;
  type_rapport: 'inspection' | 'validation' | 'intervention' | 'maintenance' | 'autre';
  template?: string;
  format_export: 'pdf' | 'docx';
  inclure_medias: boolean;
  inclure_gps: boolean;
  options?: any;
}

export interface RapportStats {
  total_rapports: number;
  rapports_ce_mois: number;
  rapports_en_attente: number;
  rapports_valides: number;
  par_type: Record<string, number>;
  par_auteur: Record<string, number>;
  taille_totale: number;
}

export interface ExportRapport {
  format: 'csv' | 'xlsx' | 'pdf';
  filtres?: {
    type_rapport?: string;
    statut?: string;
    date_debut?: string;
    date_fin?: string;
  };
  colonnes?: string[];
}

export const rapportService = {
  async getRapports(
    page: number = 1,
    size: number = 10,
    intervention_id?: string,
    type_rapport?: string,
    statut?: string,
    auteur?: string,
    date_debut?: string,
    date_fin?: string,
    search?: string
  ): Promise<RapportListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
    });
    
    if (intervention_id) params.append('intervention_id', intervention_id);
    if (type_rapport) params.append('type_rapport', type_rapport);
    if (statut) params.append('statut', statut);
    if (auteur) params.append('auteur', auteur);
    if (date_debut) params.append('date_debut', date_debut);
    if (date_fin) params.append('date_fin', date_fin);
    if (search) params.append('search', search);
    
    const response = await api.get(`/rapports?${params.toString()}`);
    return response.data;
  },

  async getRapport(id: string): Promise<Rapport> {
    const response = await api.get(`/rapports/${id}`);
    return response.data;
  },

  async createRapport(rapportData: RapportCreate): Promise<Rapport> {
    const response = await api.post('/rapports', rapportData);
    return response.data;
  },

  async updateRapport(id: string, rapportData: RapportUpdate): Promise<Rapport> {
    const response = await api.put(`/rapports/${id}`, rapportData);
    return response.data;
  },

  async deleteRapport(id: string): Promise<void> {
    await api.delete(`/rapports/${id}`);
  },

  async generateRapport(generationData: GenerationRapport): Promise<{rapport_id: string, file_path: string, file_size: number, file_type: string}> {
    const response = await api.post('/rapports/generate', generationData);
    return response.data;
  },

  async downloadRapport(id: string): Promise<Blob> {
    const response = await api.get(`/rapports/${id}/download`, {
      responseType: 'blob'
    });
    return response.data;
  },

  async getStats(): Promise<RapportStats> {
    const response = await api.get('/rapports/stats/summary');
    return response.data;
  },

  async exportRapports(exportData: ExportRapport): Promise<Blob> {
    const response = await api.post('/rapports/export', exportData, {
      responseType: 'blob'
    });
    return response.data;
  },
};
