import React, { useState, useEffect, useContext } from 'react';
import { Button } from '../UI/Button';
import { LoadingSpinner } from '../UI/LoadingSpinner';
import { Modal } from '../UI/Modal';
import { AuthContext } from '../../contexts/AuthContext';
import { 
  checkOnlineStatus,
  prepareOfflineData,
  processSync,
  getSyncQueue,
  getSyncConflicts,
  resolveSyncConflict
} from '../../services/offlineService';

interface SyncResult {
  processed: number;
  successful: number;
  failed: number;
  conflicts: number;
  errors: string[];
}

interface SyncConflict {
  id: string;
  model: string;
  object_id: string;
  server_data: any;
  client_data: any;
  created_at: string;
}

export const OfflineManager: React.FC = () => {
  const { user } = useContext(AuthContext);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isLoading, setIsLoading] = useState(false);
  const [syncQueue, setSyncQueue] = useState<any[]>([]);
  const [conflicts, setConflicts] = useState<SyncConflict[]>([]);
  const [lastSyncResult, setLastSyncResult] = useState<SyncResult | null>(null);
  const [showConflictModal, setShowConflictModal] = useState(false);
  const [selectedConflict, setSelectedConflict] = useState<SyncConflict | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    // Set up online/offline event listeners
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Load initial data
    loadSyncQueue();
    loadSyncConflicts();

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const loadSyncQueue = async () => {
    try {
      const result = await getSyncQueue();
      if (result.success) {
        setSyncQueue(result.queue);
      }
    } catch (error) {
      console.error('Error loading sync queue:', error);
    }
  };

  const loadSyncConflicts = async () => {
    try {
      const result = await getSyncConflicts();
      if (result.success) {
        setConflicts(result.conflicts);
      }
    } catch (error) {
      console.error('Error loading sync conflicts:', error);
    }
  };

  const handlePrepareOfflineData = async () => {
    setIsLoading(true);
    setError('');

    try {
      const dataTypes = ['clients', 'interventions', 'inspections'];
      const result = await prepareOfflineData(dataTypes);
      
      if (result.success) {
        // Store data in localStorage for offline access
        localStorage.setItem('offlineData', JSON.stringify(result.data));
        localStorage.setItem('offlineDataTimestamp', new Date().toISOString());
      } else {
        setError('Failed to prepare offline data');
      }
    } catch (error) {
      setError('Error preparing offline data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSync = async () => {
    setIsLoading(true);
    setError('');

    try {
      const result = await processSync();
      if (result.success) {
        setLastSyncResult(result.sync_results);
        await loadSyncQueue();
        await loadSyncConflicts();
      } else {
        setError('Synchronization failed');
      }
    } catch (error) {
      setError('Error during synchronization');
    } finally {
      setIsLoading(false);
    }
  };

  const handleConflictResolve = (conflict: SyncConflict) => {
    setSelectedConflict(conflict);
    setShowConflictModal(true);
  };

  const resolveConflict = async (resolution: string, resolvedData?: any) => {
    if (!selectedConflict) return;

    setIsLoading(true);

    try {
      const result = await resolveSyncConflict(
        selectedConflict.id,
        resolution,
        resolvedData
      );

      if (result.success) {
        setShowConflictModal(false);
        setSelectedConflict(null);
        await loadSyncConflicts();
      } else {
        setError('Failed to resolve conflict');
      }
    } catch (error) {
      setError('Error resolving conflict');
    } finally {
      setIsLoading(false);
    }
  };

  const getOfflineDataAge = () => {
    const timestamp = localStorage.getItem('offlineDataTimestamp');
    if (!timestamp) return null;

    const age = Date.now() - new Date(timestamp).getTime();
    const hours = Math.floor(age / (1000 * 60 * 60));
    const minutes = Math.floor((age % (1000 * 60 * 60)) / (1000 * 60));

    if (hours > 0) {
      return `${hours}h ${minutes}m ago`;
    }
    return `${minutes}m ago`;
  };

  return (
    <div className="space-y-6">
      {/* Connection Status */}
      <div className="border rounded-lg p-4">
        <h3 className="text-lg font-medium mb-4">Connection Status</h3>
        <div className="flex items-center space-x-3">
          <div className={`w-3 h-3 rounded-full ${
            isOnline ? 'bg-green-500' : 'bg-red-500'
          }`}></div>
          <span className={`font-medium ${
            isOnline ? 'text-green-700' : 'text-red-700'
          }`}>
            {isOnline ? 'Online' : 'Offline'}
          </span>
        </div>
        {!isOnline && (
          <p className="text-sm text-gray-600 mt-2">
            You are currently offline. Changes will be synchronized when connection is restored.
          </p>
        )}
      </div>

      {/* Offline Data Management */}
      <div className="border rounded-lg p-4">
        <h3 className="text-lg font-medium mb-4">Offline Data</h3>
        
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Offline Data Cache</p>
              {getOfflineDataAge() && (
                <p className="text-sm text-gray-600">
                  Last updated: {getOfflineDataAge()}
                </p>
              )}
            </div>
            <Button
              onClick={handlePrepareOfflineData}
              disabled={isLoading || !isOnline}
              className="flex items-center space-x-2"
            >
              {isLoading ? (
                <LoadingSpinner size="sm" />
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
                </svg>
              )}
              <span>Update Cache</span>
            </Button>
          </div>
        </div>
      </div>

      {/* Sync Queue */}
      <div className="border rounded-lg p-4">
        <h3 className="text-lg font-medium mb-4">Pending Changes</h3>
        
        {syncQueue.length > 0 ? (
          <div className="space-y-3">
            <p className="text-sm text-gray-600">
              {syncQueue.length} change(s) pending synchronization
            </p>
            
            <div className="bg-gray-50 rounded p-3 max-h-40 overflow-y-auto">
              {syncQueue.map((item, index) => (
                <div key={index} className="flex items-center justify-between py-1 text-sm">
                  <span>
                    {item.action} {item.data_type} ({item.object_id})
                  </span>
                  <span className="text-gray-500">
                    {new Date(item.created_at).toLocaleString()}
                  </span>
                </div>
              ))}
            </div>

            <div className="flex items-center space-x-2">
              <Button
                onClick={handleSync}
                disabled={isLoading || !isOnline}
                className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700"
              >
                {isLoading ? (
                  <LoadingSpinner size="sm" />
                ) : (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                )}
                <span>Sync Now</span>
              </Button>
              
              {!isOnline && (
                <p className="text-sm text-gray-500">
                  Sync will be performed when online
                </p>
              )}
            </div>
          </div>
        ) : (
          <p className="text-gray-500">No pending changes</p>
        )}
      </div>

      {/* Sync Results */}
      {lastSyncResult && (
        <div className="border rounded-lg p-4">
          <h3 className="text-lg font-medium mb-4">Last Sync Results</h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {lastSyncResult.processed}
              </div>
              <div className="text-sm text-gray-600">Processed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {lastSyncResult.successful}
              </div>
              <div className="text-sm text-gray-600">Successful</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {lastSyncResult.failed}
              </div>
              <div className="text-sm text-gray-600">Failed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">
                {lastSyncResult.conflicts}
              </div>
              <div className="text-sm text-gray-600">Conflicts</div>
            </div>
          </div>

          {lastSyncResult.errors.length > 0 && (
            <div className="mt-4 bg-red-50 border border-red-200 rounded p-3">
              <h4 className="font-medium text-red-900 mb-2">Errors:</h4>
              <ul className="text-sm text-red-800 list-disc list-inside">
                {lastSyncResult.errors.map((error, index) => (
                  <li key={index}>{error}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Conflicts */}
      {conflicts.length > 0 && (
        <div className="border rounded-lg p-4">
          <h3 className="text-lg font-medium mb-4">Sync Conflicts</h3>
          
          <div className="space-y-3">
            {conflicts.map((conflict) => (
              <div key={conflict.id} className="bg-yellow-50 border border-yellow-200 rounded p-3">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-yellow-900">
                      {conflict.model} ({conflict.object_id})
                    </p>
                    <p className="text-sm text-yellow-800">
                      Conflict detected on {new Date(conflict.created_at).toLocaleString()}
                    </p>
                  </div>
                  <Button
                    onClick={() => handleConflictResolve(conflict)}
                    className="bg-yellow-600 hover:bg-yellow-700 text-white"
                  >
                    Resolve
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded p-3">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Conflict Resolution Modal */}
      <Modal
        isOpen={showConflictModal}
        onClose={() => setShowConflictModal(false)}
        title="Resolve Sync Conflict"
      >
        {selectedConflict && (
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              Choose how to resolve the conflict for {selectedConflict.model} ({selectedConflict.object_id}):
            </p>

            <div className="grid grid-cols-2 gap-4">
              <div className="border rounded p-3">
                <h4 className="font-medium text-gray-900 mb-2">Server Version</h4>
                <pre className="text-xs bg-gray-50 p-2 rounded overflow-auto max-h-32">
                  {JSON.stringify(selectedConflict.server_data, null, 2)}
                </pre>
                <Button
                  onClick={() => resolveConflict('use_server')}
                  className="mt-2 w-full bg-blue-600 hover:bg-blue-700"
                  disabled={isLoading}
                >
                  Use Server Version
                </Button>
              </div>

              <div className="border rounded p-3">
                <h4 className="font-medium text-gray-900 mb-2">Local Version</h4>
                <pre className="text-xs bg-gray-50 p-2 rounded overflow-auto max-h-32">
                  {JSON.stringify(selectedConflict.client_data, null, 2)}
                </pre>
                <Button
                  onClick={() => resolveConflict('use_client')}
                  className="mt-2 w-full bg-green-600 hover:bg-green-700"
                  disabled={isLoading}
                >
                  Use Local Version
                </Button>
              </div>
            </div>

            {isLoading && (
              <div className="flex items-center justify-center py-4">
                <LoadingSpinner />
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};
