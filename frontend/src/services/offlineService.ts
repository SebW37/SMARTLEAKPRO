import { api } from './api';

export interface OfflineData {
  [key: string]: any[];
}

export interface PrepareOfflineResult {
  success: boolean;
  data?: OfflineData;
  user_id?: number;
  prepared_types?: string[];
  error?: string;
}

export interface SyncQueueItem {
  id: string;
  action: 'create' | 'update' | 'delete';
  data_type: string;
  object_id: string;
  data: any;
  created_at: string;
  user_id: number;
  status: 'pending' | 'processed' | 'failed';
}

export interface SyncResult {
  processed: number;
  successful: number;
  failed: number;
  conflicts: number;
  errors: string[];
  sync_results?: any;
}

export interface SyncConflict {
  id: string;
  model: string;
  object_id: string;
  server_data: any;
  client_data: any;
  created_at: string;
}

export interface OfflineServiceResult {
  success: boolean;
  message?: string;
  data?: any;
  queue?: SyncQueueItem[];
  conflicts?: SyncConflict[];
  count?: number;
  error?: string;
}

export interface OnlineStatusResult {
  success: boolean;
  online: boolean;
  timestamp: string;
  error?: string;
}

// Offline data preparation
export const prepareOfflineData = async (dataTypes: string[]): Promise<PrepareOfflineResult> => {
  try {
    const response = await api.post('/core/offline/prepare/', {
      data_types: dataTypes
    });
    return response.data;
  } catch (error: any) {
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to prepare offline data'
    };
  }
};

export const storeOfflineData = async (
  dataType: string,
  objectId: string,
  data: any
): Promise<OfflineServiceResult> => {
  try {
    const response = await api.post('/core/offline/store/', {
      data_type: dataType,
      object_id: objectId,
      data
    });
    return response.data;
  } catch (error: any) {
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to store offline data'
    };
  }
};

export const getOfflineData = async (dataType?: string): Promise<OfflineServiceResult> => {
  try {
    const params = dataType ? { data_type: dataType } : {};
    const response = await api.get('/core/offline/data/', { params });
    return response.data;
  } catch (error: any) {
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to get offline data'
    };
  }
};

// Sync queue management
export const queueSyncAction = async (
  action: 'create' | 'update' | 'delete',
  dataType: string,
  objectId: string,
  data?: any
): Promise<OfflineServiceResult> => {
  try {
    const response = await api.post('/core/offline/queue/', {
      action,
      data_type: dataType,
      object_id: objectId,
      data: data || {}
    });
    return response.data;
  } catch (error: any) {
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to queue sync action'
    };
  }
};

export const getSyncQueue = async (): Promise<OfflineServiceResult> => {
  try {
    const response = await api.get('/core/offline/queue/');
    return response.data;
  } catch (error: any) {
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to get sync queue'
    };
  }
};

export const processSync = async (): Promise<OfflineServiceResult> => {
  try {
    const response = await api.post('/core/offline/sync/');
    return response.data;
  } catch (error: any) {
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to process sync'
    };
  }
};

export const bulkSyncData = async (syncItems: any[]): Promise<OfflineServiceResult> => {
  try {
    const response = await api.post('/core/offline/bulk-sync/', {
      sync_items: syncItems
    });
    return response.data;
  } catch (error: any) {
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to bulk sync data'
    };
  }
};

// Conflict resolution
export const getSyncConflicts = async (): Promise<OfflineServiceResult> => {
  try {
    const response = await api.get('/core/offline/conflicts/');
    return response.data;
  } catch (error: any) {
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to get sync conflicts'
    };
  }
};

export const resolveSyncConflict = async (
  conflictId: string,
  resolution: 'use_server' | 'use_client' | 'merge',
  resolvedData?: any
): Promise<OfflineServiceResult> => {
  try {
    const response = await api.post('/core/offline/conflicts/resolve/', {
      conflict_id: conflictId,
      resolution,
      resolved_data: resolvedData || {}
    });
    return response.data;
  } catch (error: any) {
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to resolve sync conflict'
    };
  }
};

// Online status
export const checkOnlineStatus = async (): Promise<OnlineStatusResult> => {
  try {
    const response = await api.get('/core/offline/status/');
    return response.data;
  } catch (error: any) {
    return {
      success: false,
      online: false,
      timestamp: new Date().toISOString(),
      error: error.response?.data?.error || 'Failed to check online status'
    };
  }
};

// Local storage utilities for offline functionality
export class OfflineStorageManager {
  private static readonly STORAGE_PREFIX = 'smartleakpro_offline_';
  private static readonly DATA_KEY = `${this.STORAGE_PREFIX}data`;
  private static readonly QUEUE_KEY = `${this.STORAGE_PREFIX}queue`;
  private static readonly TIMESTAMP_KEY = `${this.STORAGE_PREFIX}timestamp`;

  static storeData(data: OfflineData): void {
    try {
      localStorage.setItem(this.DATA_KEY, JSON.stringify(data));
      localStorage.setItem(this.TIMESTAMP_KEY, new Date().toISOString());
    } catch (error) {
      console.error('Failed to store offline data:', error);
    }
  }

  static getData(): OfflineData | null {
    try {
      const data = localStorage.getItem(this.DATA_KEY);
      return data ? JSON.parse(data) : null;
    } catch (error) {
      console.error('Failed to get offline data:', error);
      return null;
    }
  }

  static getDataTimestamp(): Date | null {
    try {
      const timestamp = localStorage.getItem(this.TIMESTAMP_KEY);
      return timestamp ? new Date(timestamp) : null;
    } catch (error) {
      console.error('Failed to get data timestamp:', error);
      return null;
    }
  }

  static clearData(): void {
    try {
      localStorage.removeItem(this.DATA_KEY);
      localStorage.removeItem(this.TIMESTAMP_KEY);
    } catch (error) {
      console.error('Failed to clear offline data:', error);
    }
  }

  static addToQueue(item: Omit<SyncQueueItem, 'id' | 'created_at' | 'user_id' | 'status'>): void {
    try {
      const queue = this.getQueue();
      const newItem: SyncQueueItem = {
        ...item,
        id: `${item.data_type}_${item.object_id}_${Date.now()}`,
        created_at: new Date().toISOString(),
        user_id: 0, // Will be set by the server
        status: 'pending'
      };
      queue.push(newItem);
      localStorage.setItem(this.QUEUE_KEY, JSON.stringify(queue));
    } catch (error) {
      console.error('Failed to add to sync queue:', error);
    }
  }

  static getQueue(): SyncQueueItem[] {
    try {
      const queue = localStorage.getItem(this.QUEUE_KEY);
      return queue ? JSON.parse(queue) : [];
    } catch (error) {
      console.error('Failed to get sync queue:', error);
      return [];
    }
  }

  static clearQueue(): void {
    try {
      localStorage.removeItem(this.QUEUE_KEY);
    } catch (error) {
      console.error('Failed to clear sync queue:', error);
    }
  }

  static removeFromQueue(itemId: string): void {
    try {
      const queue = this.getQueue();
      const filteredQueue = queue.filter(item => item.id !== itemId);
      localStorage.setItem(this.QUEUE_KEY, JSON.stringify(filteredQueue));
    } catch (error) {
      console.error('Failed to remove from sync queue:', error);
    }
  }

  static updateQueueItem(itemId: string, updates: Partial<SyncQueueItem>): void {
    try {
      const queue = this.getQueue();
      const itemIndex = queue.findIndex(item => item.id === itemId);
      if (itemIndex !== -1) {
        queue[itemIndex] = { ...queue[itemIndex], ...updates };
        localStorage.setItem(this.QUEUE_KEY, JSON.stringify(queue));
      }
    } catch (error) {
      console.error('Failed to update queue item:', error);
    }
  }

  static getQueueCount(): number {
    return this.getQueue().length;
  }

  static getPendingQueueCount(): number {
    return this.getQueue().filter(item => item.status === 'pending').length;
  }
}

// Network status utilities
export class NetworkStatusManager {
  private static listeners: Array<(isOnline: boolean) => void> = [];

  static init(): void {
    window.addEventListener('online', () => this.notifyListeners(true));
    window.addEventListener('offline', () => this.notifyListeners(false));
  }

  static isOnline(): boolean {
    return navigator.onLine;
  }

  static addListener(listener: (isOnline: boolean) => void): void {
    this.listeners.push(listener);
  }

  static removeListener(listener: (isOnline: boolean) => void): void {
    this.listeners = this.listeners.filter(l => l !== listener);
  }

  private static notifyListeners(isOnline: boolean): void {
    this.listeners.forEach(listener => listener(isOnline));
  }
}

// Auto-sync functionality
export class AutoSyncManager {
  private static syncInterval: NodeJS.Timeout | null = null;
  private static isAutoSyncEnabled = false;

  static enable(intervalMs: number = 30000): void {
    if (this.isAutoSyncEnabled) {
      this.disable();
    }

    this.isAutoSyncEnabled = true;
    this.syncInterval = setInterval(async () => {
      if (NetworkStatusManager.isOnline() && OfflineStorageManager.getPendingQueueCount() > 0) {
        try {
          await this.performAutoSync();
        } catch (error) {
          console.error('Auto-sync failed:', error);
        }
      }
    }, intervalMs);
  }

  static disable(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }
    this.isAutoSyncEnabled = false;
  }

  static isEnabled(): boolean {
    return this.isAutoSyncEnabled;
  }

  private static async performAutoSync(): Promise<void> {
    const queue = OfflineStorageManager.getQueue();
    const pendingItems = queue.filter(item => item.status === 'pending');

    if (pendingItems.length === 0) {
      return;
    }

    try {
      const result = await bulkSyncData(pendingItems);
      if (result.success) {
        // Clear successfully synced items
        OfflineStorageManager.clearQueue();
      }
    } catch (error) {
      console.error('Auto-sync error:', error);
    }
  }
}

// Initialize network status manager
NetworkStatusManager.init();
