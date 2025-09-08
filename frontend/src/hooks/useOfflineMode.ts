import { useState, useEffect, useCallback } from 'react';
import { 
  NetworkStatusManager, 
  OfflineStorageManager, 
  AutoSyncManager,
  checkOnlineStatus,
  processSync
} from '../services';

interface OfflineModeState {
  isOnline: boolean;
  isOfflineMode: boolean;
  lastSyncTime: Date | null;
  pendingChanges: number;
  isSyncing: boolean;
  syncError: string | null;
}

export const useOfflineMode = () => {
  const [state, setState] = useState<OfflineModeState>({
    isOnline: NetworkStatusManager.isOnline(),
    isOfflineMode: false,
    lastSyncTime: null,
    pendingChanges: 0,
    isSyncing: false,
    syncError: null
  });

  const updateOnlineStatus = useCallback((isOnline: boolean) => {
    setState(prev => ({
      ...prev,
      isOnline,
      isOfflineMode: !isOnline
    }));
  }, []);

  const updatePendingChanges = useCallback(() => {
    const pendingCount = OfflineStorageManager.getPendingQueueCount();
    setState(prev => ({
      ...prev,
      pendingChanges: pendingCount
    }));
  }, []);

  const performSync = useCallback(async () => {
    if (!state.isOnline || state.isSyncing) return;

    setState(prev => ({ ...prev, isSyncing: true, syncError: null }));

    try {
      const result = await processSync();
      if (result.success) {
        setState(prev => ({
          ...prev,
          lastSyncTime: new Date(),
          pendingChanges: 0
        }));
      } else {
        setState(prev => ({
          ...prev,
          syncError: result.error || 'Erreur de synchronisation'
        }));
      }
    } catch (error: any) {
      setState(prev => ({
        ...prev,
        syncError: error.message || 'Erreur de synchronisation'
      }));
    } finally {
      setState(prev => ({ ...prev, isSyncing: false }));
    }
  }, [state.isOnline, state.isSyncing]);

  const enableAutoSync = useCallback((intervalMs: number = 30000) => {
    AutoSyncManager.enable(intervalMs);
  }, []);

  const disableAutoSync = useCallback(() => {
    AutoSyncManager.disable();
  }, []);

  const clearSyncError = useCallback(() => {
    setState(prev => ({ ...prev, syncError: null }));
  }, []);

  const prepareOfflineData = useCallback(async (dataTypes: string[]) => {
    try {
      // This would typically call the API to prepare offline data
      // For now, we'll just update the last sync time
      setState(prev => ({
        ...prev,
        lastSyncTime: new Date()
      }));
    } catch (error) {
      console.error('Error preparing offline data:', error);
    }
  }, []);

  useEffect(() => {
    // Listen for network status changes
    NetworkStatusManager.addListener(updateOnlineStatus);

    // Check initial online status
    checkOnlineStatus().then(result => {
      if (result.success) {
        updateOnlineStatus(result.online);
      }
    });

    // Update pending changes count
    updatePendingChanges();

    // Set up interval to check pending changes
    const interval = setInterval(updatePendingChanges, 5000);

    return () => {
      NetworkStatusManager.removeListener(updateOnlineStatus);
      clearInterval(interval);
    };
  }, [updateOnlineStatus, updatePendingChanges]);

  useEffect(() => {
    // Auto-sync when coming back online
    if (state.isOnline && state.pendingChanges > 0 && !state.isSyncing) {
      const timeoutId = setTimeout(() => {
        performSync();
      }, 2000); // Wait 2 seconds after coming online

      return () => clearTimeout(timeoutId);
    }
  }, [state.isOnline, state.pendingChanges, state.isSyncing, performSync]);

  return {
    ...state,
    performSync,
    enableAutoSync,
    disableAutoSync,
    clearSyncError,
    prepareOfflineData,
    updatePendingChanges
  };
};
