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

export interface Media {
  id: string;
  intervention_id: string;
  inspection_id?: string;
  nom_fichier: string;
  nom_original: string;
  type_media: 'photo' | 'video' | 'audio' | 'document' | 'autre';
  statut: 'uploading' | 'uploaded' | 'processing' | 'ready' | 'error' | 'deleted';
  url_fichier: string;
  taille_fichier: number;
  mime_type?: string;
  hash_fichier?: string;
  latitude?: string;
  longitude?: string;
  precision_gps?: string;
  altitude?: string;
  date_prise?: string;
  date_upload: string;
  date_modification?: string;
  meta_exif?: any;
  resolution_x?: number;
  resolution_y?: number;
  duree?: number;
  annotations?: string;
  description?: string;
  tags?: string[];
  version: string;
  parent_id?: string;
  est_version: boolean;
  utilisateur_upload?: string;
  appareil_info?: string;
  mode_capture?: string;
}

export interface MediaThumbnail {
  id: string;
  nom_fichier: string;
  type_media: 'photo' | 'video' | 'audio' | 'document' | 'autre';
  statut: 'uploading' | 'uploaded' | 'processing' | 'ready' | 'error' | 'deleted';
  url_fichier: string;
  taille_fichier: number;
  date_prise?: string;
  annotations?: string;
  description?: string;
  latitude?: string;
  longitude?: string;
  resolution_x?: number;
  resolution_y?: number;
  duree?: number;
}

export interface MediaListResponse {
  medias: MediaThumbnail[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface MediaUploadData {
  intervention_id: string;
  inspection_id?: string;
  type_media: 'photo' | 'video' | 'audio' | 'document' | 'autre';
  annotations?: string;
  description?: string;
  latitude?: string;
  longitude?: string;
  precision_gps?: string;
  altitude?: string;
  date_prise?: string;
  appareil_info?: string;
  mode_capture?: string;
}

export interface MediaUploadResponse {
  media_id: string;
  upload_url?: string;
  status: string;
  message: string;
}

export interface MediaStats {
  total_medias: number;
  medias_ce_mois: number;
  medias_en_attente: number;
  medias_ready: number;
  par_type: Record<string, number>;
  par_intervention: Record<string, number>;
  taille_totale: number;
  medias_avec_gps: number;
  medias_avec_annotations: number;
}

export interface MediaSearch {
  query?: string;
  type_media?: 'photo' | 'video' | 'audio' | 'document' | 'autre';
  intervention_id?: string;
  date_debut?: string;
  date_fin?: string;
  avec_gps?: boolean;
  avec_annotations?: boolean;
  tags?: string[];
}

export const mediaService = {
  async getMedias(
    page: number = 1,
    size: number = 10,
    intervention_id?: string,
    inspection_id?: string,
    type_media?: string,
    statut?: string,
    avec_gps?: boolean,
    avec_annotations?: boolean,
    date_debut?: string,
    date_fin?: string,
    search?: string
  ): Promise<MediaListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      size: size.toString(),
    });
    
    if (intervention_id) params.append('intervention_id', intervention_id);
    if (inspection_id) params.append('inspection_id', inspection_id);
    if (type_media) params.append('type_media', type_media);
    if (statut) params.append('statut', statut);
    if (avec_gps !== undefined) params.append('avec_gps', avec_gps.toString());
    if (avec_annotations !== undefined) params.append('avec_annotations', avec_annotations.toString());
    if (date_debut) params.append('date_debut', date_debut);
    if (date_fin) params.append('date_fin', date_fin);
    if (search) params.append('search', search);
    
    const response = await api.get(`/medias?${params.toString()}`);
    return response.data;
  },

  async getMedia(id: string): Promise<Media> {
    const response = await api.get(`/medias/${id}`);
    return response.data;
  },

  async uploadMedia(
    file: File,
    uploadData: MediaUploadData,
    onProgress?: (progress: number) => void
  ): Promise<MediaUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('intervention_id', uploadData.intervention_id);
    formData.append('type_media', uploadData.type_media);
    
    if (uploadData.inspection_id) formData.append('inspection_id', uploadData.inspection_id);
    if (uploadData.annotations) formData.append('annotations', uploadData.annotations);
    if (uploadData.description) formData.append('description', uploadData.description);
    if (uploadData.latitude) formData.append('latitude', uploadData.latitude);
    if (uploadData.longitude) formData.append('longitude', uploadData.longitude);
    if (uploadData.precision_gps) formData.append('precision_gps', uploadData.precision_gps);
    if (uploadData.altitude) formData.append('altitude', uploadData.altitude);
    if (uploadData.date_prise) formData.append('date_prise', uploadData.date_prise);
    if (uploadData.appareil_info) formData.append('appareil_info', uploadData.appareil_info);
    if (uploadData.mode_capture) formData.append('mode_capture', uploadData.mode_capture);

    const response = await api.post('/medias/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });
    return response.data;
  },

  async updateMedia(id: string, mediaData: Partial<Media>): Promise<Media> {
    const response = await api.put(`/medias/${id}`, mediaData);
    return response.data;
  },

  async deleteMedia(id: string): Promise<void> {
    await api.delete(`/medias/${id}`);
  },

  async downloadMedia(id: string): Promise<Blob> {
    const response = await api.get(`/medias/${id}/download`, {
      responseType: 'blob'
    });
    return response.data;
  },

  async getMediaThumbnail(id: string): Promise<Blob> {
    const response = await api.get(`/medias/${id}/thumbnail`, {
      responseType: 'blob'
    });
    return response.data;
  },

  async getStats(): Promise<MediaStats> {
    const response = await api.get('/medias/stats/summary');
    return response.data;
  },

  async batchOperation(mediaIds: string[], operation: string, parameters?: any): Promise<{message: string, count: number}> {
    const response = await api.post('/medias/batch-operation', {
      media_ids: mediaIds,
      operation,
      parameters
    });
    return response.data;
  },

  // Utilitaires
  getMediaUrl(media: MediaThumbnail): string {
    return `${API_BASE_URL}${media.url_fichier}`;
  },

  getThumbnailUrl(media: MediaThumbnail): string {
    return `${API_BASE_URL}/medias/${media.id}/thumbnail`;
  },

  getDownloadUrl(media: MediaThumbnail): string {
    return `${API_BASE_URL}/medias/${media.id}/download`;
  },

  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  },

  formatDuration(seconds: number): string {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    } else {
      return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }
  },

  isImage(type: string): boolean {
    return type === 'photo';
  },

  isVideo(type: string): boolean {
    return type === 'video';
  },

  isAudio(type: string): boolean {
    return type === 'audio';
  },

  isDocument(type: string): boolean {
    return type === 'document';
  },

  getMediaIcon(type: string): string {
    switch (type) {
      case 'photo': return 'fas fa-image';
      case 'video': return 'fas fa-video';
      case 'audio': return 'fas fa-volume-up';
      case 'document': return 'fas fa-file-alt';
      default: return 'fas fa-file';
    }
  }
};
