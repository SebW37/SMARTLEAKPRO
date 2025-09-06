import { apiService } from './api';
import { Notification, ApiResponse } from '../types';

class NotificationService {
  async getNotifications(page = 1): Promise<ApiResponse<Notification>> {
    const params = new URLSearchParams();
    params.append('page', page.toString());
    
    return apiService.get<ApiResponse<Notification>>(`/notifications/?${params.toString()}`);
  }

  async getNotification(id: number): Promise<Notification> {
    return apiService.get<Notification>(`/notifications/${id}/`);
  }

  async getUnreadNotifications(): Promise<Notification[]> {
    return apiService.get<Notification[]>('/notifications/unread/');
  }

  async markNotificationsAsRead(notificationIds: number[]): Promise<{ message: string }> {
    return apiService.post<{ message: string }>('/notifications/mark-read/', {
      notification_ids: notificationIds,
    });
  }

  async sendNotification(data: {
    title: string;
    message: string;
    notification_type: 'email' | 'sms' | 'push' | 'in_app';
    recipient: number;
    template?: number;
    related_object_type?: string;
    related_object_id?: number;
    data?: Record<string, any>;
  }): Promise<{ message: string; notification_id: number }> {
    return apiService.post<{ message: string; notification_id: number }>('/notifications/send/', data);
  }

  async getNotificationStats(): Promise<Record<string, any>> {
    return apiService.get<Record<string, any>>('/notifications/stats/');
  }
}

export const notificationService = new NotificationService();
