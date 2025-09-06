// User types
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: 'admin' | 'manager' | 'technician' | 'client';
  phone?: string;
  avatar?: string;
  is_verified: boolean;
  is_active: boolean;
  date_joined: string;
  last_login?: string;
}

// Client types
export interface Client {
  id: number;
  name: string;
  client_type: 'individual' | 'company' | 'public';
  email?: string;
  phone?: string;
  address: string;
  city: string;
  postal_code: string;
  country: string;
  location?: {
    lat: number;
    lng: number;
  };
  notes?: string;
  is_active: boolean;
  created_by_name?: string;
  sites_count?: number;
  created_at: string;
  updated_at: string;
}

export interface ClientSite {
  id: number;
  client: number;
  client_name?: string;
  name: string;
  description?: string;
  address: string;
  city: string;
  postal_code: string;
  country: string;
  location?: {
    lat: number;
    lng: number;
  };
  contact_name?: string;
  contact_phone?: string;
  contact_email?: string;
  access_instructions?: string;
  notes?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Intervention types
export interface Intervention {
  id: number;
  title: string;
  description: string;
  intervention_type: 'inspection' | 'repair' | 'maintenance' | 'emergency' | 'other';
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled' | 'postponed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  client: number;
  site?: number;
  client_name?: string;
  site_name?: string;
  scheduled_date: string;
  estimated_duration?: string;
  actual_start_date?: string;
  actual_end_date?: string;
  assigned_technician?: number;
  assigned_technician_name?: string;
  created_by?: number;
  created_by_name?: string;
  location?: {
    lat: number;
    lng: number;
  };
  address?: string;
  notes?: string;
  materials_needed?: string;
  special_instructions?: string;
  is_overdue?: boolean;
  duration?: string;
  created_at: string;
  updated_at: string;
}

// Inspection types
export interface Inspection {
  id: number;
  title: string;
  description?: string;
  status: 'draft' | 'in_progress' | 'completed' | 'validated' | 'rejected';
  template?: number;
  form_data: Record<string, any>;
  client: number;
  site?: number;
  client_name?: string;
  site_name?: string;
  intervention?: number;
  location?: {
    lat: number;
    lng: number;
  };
  address?: string;
  inspection_date: string;
  started_at?: string;
  completed_at?: string;
  inspector?: number;
  inspector_name?: string;
  created_by?: number;
  created_by_name?: string;
  score?: number;
  max_score?: number;
  compliance_status?: string;
  score_percentage?: number;
  notes?: string;
  recommendations?: string;
  duration?: string;
  created_at: string;
  updated_at: string;
}

export interface InspectionItem {
  id: number;
  template_item_id?: string;
  label: string;
  item_type: 'text' | 'number' | 'boolean' | 'choice' | 'photo' | 'video' | 'audio' | 'signature' | 'location';
  value?: string;
  is_required: boolean;
  order: number;
  show_condition: Record<string, any>;
  location?: {
    lat: number;
    lng: number;
  };
  created_at: string;
  updated_at: string;
}

// Report types
export interface Report {
  id: number;
  title: string;
  description?: string;
  status: 'generating' | 'completed' | 'failed' | 'archived';
  format: 'pdf' | 'docx' | 'html' | 'xlsx';
  template?: number;
  content: Record<string, any>;
  client?: number;
  client_name?: string;
  intervention?: number;
  intervention_title?: string;
  inspection?: number;
  inspection_title?: string;
  file?: string;
  file_url?: string;
  file_size?: number;
  generated_at?: string;
  generation_duration?: string;
  created_by_name?: string;
  created_at: string;
  updated_at: string;
}

// Notification types
export interface Notification {
  id: number;
  title: string;
  message: string;
  notification_type: 'email' | 'sms' | 'push' | 'in_app';
  status: 'pending' | 'sent' | 'delivered' | 'failed' | 'read';
  recipient: number;
  recipient_name?: string;
  template?: number;
  template_name?: string;
  related_object_type?: string;
  related_object_id?: number;
  sent_at?: string;
  delivered_at?: string;
  read_at?: string;
  error_message?: string;
  retry_count: number;
  data: Record<string, any>;
  created_at: string;
  updated_at: string;
}

// API Response types
export interface ApiResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

export interface ApiError {
  detail?: string;
  message?: string;
  errors?: Record<string, string[]>;
}

// Form types
export interface LoginForm {
  username: string;
  password: string;
}

export interface ClientForm {
  name: string;
  client_type: 'individual' | 'company' | 'public';
  email?: string;
  phone?: string;
  address: string;
  city: string;
  postal_code: string;
  country: string;
  notes?: string;
  is_active: boolean;
}

export interface InterventionForm {
  title: string;
  description: string;
  intervention_type: 'inspection' | 'repair' | 'maintenance' | 'emergency' | 'other';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  client: number;
  site?: number;
  scheduled_date: string;
  estimated_duration?: string;
  assigned_technician?: number;
  address?: string;
  notes?: string;
  materials_needed?: string;
  special_instructions?: string;
}

// Filter types
export interface ClientFilters {
  client_type?: string;
  is_active?: boolean;
  city?: string;
  search?: string;
}

export interface InterventionFilters {
  status?: string;
  priority?: string;
  intervention_type?: string;
  client?: number;
  assigned_technician?: number;
  search?: string;
}

export interface InspectionFilters {
  status?: string;
  client?: number;
  site?: number;
  inspector?: number;
  template?: number;
  search?: string;
}

// Chart data types
export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string | string[];
    borderWidth?: number;
  }[];
}

// Statistics types
export interface DashboardStats {
  total_clients: number;
  active_clients: number;
  total_interventions: number;
  scheduled_interventions: number;
  in_progress_interventions: number;
  completed_interventions: number;
  overdue_interventions: number;
  total_inspections: number;
  completed_inspections: number;
  total_reports: number;
  unread_notifications: number;
}

// Map types
export interface MapMarker {
  id: number;
  position: {
    lat: number;
    lng: number;
  };
  title: string;
  description?: string;
  type: 'client' | 'intervention' | 'inspection';
  status?: string;
}
