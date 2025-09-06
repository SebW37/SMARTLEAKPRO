import { apiService } from './api';
import { User, LoginForm } from '../types';

interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
}

class AuthService {
  async login(credentials: LoginForm): Promise<LoginResponse> {
    return apiService.post<LoginResponse>('/auth/login/', credentials);
  }

  async logout(): Promise<void> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      try {
        await apiService.post('/auth/logout/', { refresh: refreshToken });
      } catch (error) {
        // Ignore logout errors
        console.error('Logout error:', error);
      }
    }
  }

  async getProfile(): Promise<User> {
    return apiService.get<User>('/auth/profile/');
  }

  async updateProfile(data: Partial<User>): Promise<User> {
    return apiService.patch<User>('/auth/profile/update/', data);
  }

  async refreshToken(): Promise<{ access: string }> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }
    return apiService.post<{ access: string }>('/auth/token/refresh/', {
      refresh: refreshToken,
    });
  }
}

export const authService = new AuthService();
