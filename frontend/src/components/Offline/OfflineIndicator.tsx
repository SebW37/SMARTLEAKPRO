import React from 'react';
import { useOfflineMode } from '../../hooks/useOfflineMode';
import { Button } from '../UI/Button';

export const OfflineIndicator: React.FC = () => {
  const {
    isOnline,
    isOfflineMode,
    pendingChanges,
    isSyncing,
    syncError,
    performSync,
    clearSyncError
  } = useOfflineMode();

  if (!isOfflineMode && pendingChanges === 0 && !syncError) {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* Offline Mode Indicator */}
      {isOfflineMode && (
        <div className="bg-yellow-500 text-white px-4 py-2 rounded-lg shadow-lg mb-2 flex items-center space-x-2">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <span className="text-sm font-medium">Mode hors-ligne</span>
        </div>
      )}

      {/* Pending Changes Indicator */}
      {pendingChanges > 0 && (
        <div className="bg-blue-500 text-white px-4 py-2 rounded-lg shadow-lg mb-2 flex items-center space-x-2">
          <div className="flex items-center space-x-2">
            {isSyncing ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            )}
            <span className="text-sm font-medium">
              {isSyncing ? 'Synchronisation...' : `${pendingChanges} modification(s) en attente`}
            </span>
          </div>
          
          {isOnline && !isSyncing && (
            <Button
              onClick={performSync}
              size="sm"
              className="bg-white text-blue-500 hover:bg-blue-50"
            >
              Sync
            </Button>
          )}
        </div>
      )}

      {/* Sync Error Indicator */}
      {syncError && (
        <div className="bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg mb-2 flex items-center space-x-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
          <span className="text-sm font-medium flex-1">{syncError}</span>
          <Button
            onClick={clearSyncError}
            size="sm"
            className="bg-white text-red-500 hover:bg-red-50"
          >
            ×
          </Button>
        </div>
      )}

      {/* Online Status Indicator */}
      {isOnline && pendingChanges === 0 && !syncError && (
        <div className="bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg flex items-center space-x-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          <span className="text-sm font-medium">En ligne</span>
        </div>
      )}
    </div>
  );
};
