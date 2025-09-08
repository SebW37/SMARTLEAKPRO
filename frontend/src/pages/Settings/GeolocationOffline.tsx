import React, { useState, useEffect } from 'react';
import { Layout } from '../../components/Layout/Layout';
import { LocationPicker } from '../../components/Geolocation/LocationPicker';
import { OfflineManager } from '../../components/Offline/OfflineManager';
import { Button } from '../../components/UI/Button';
import { Modal } from '../../components/UI/Modal';
import { 
  getCurrentPosition, 
  findNearby,
  OfflineStorageManager,
  NetworkStatusManager
} from '../../services';

interface Location {
  latitude: number;
  longitude: number;
}

export const GeolocationOffline: React.FC = () => {
  const [currentLocation, setCurrentLocation] = useState<Location | null>(null);
  const [nearbyClients, setNearbyClients] = useState<any[]>([]);
  const [isNearbyModalOpen, setIsNearbyModalOpen] = useState(false);
  const [isOnline, setIsOnline] = useState(NetworkStatusManager.isOnline());
  const [offlineDataAge, setOfflineDataAge] = useState<string>('');

  useEffect(() => {
    // Listen for network status changes
    const handleNetworkChange = (online: boolean) => {
      setIsOnline(online);
    };

    NetworkStatusManager.addListener(handleNetworkChange);

    // Check offline data age
    const timestamp = OfflineStorageManager.getDataTimestamp();
    if (timestamp) {
      const age = Date.now() - timestamp.getTime();
      const hours = Math.floor(age / (1000 * 60 * 60));
      const minutes = Math.floor((age % (1000 * 60 * 60)) / (1000 * 60));
      setOfflineDataAge(hours > 0 ? `${hours}h ${minutes}m ago` : `${minutes}m ago`);
    }

    return () => {
      NetworkStatusManager.removeListener(handleNetworkChange);
    };
  }, []);

  const handleLocationChange = (location: Location) => {
    setCurrentLocation(location);
  };

  const handleFindNearby = async () => {
    if (!currentLocation) return;

    try {
      const result = await findNearby(
        currentLocation.latitude,
        currentLocation.longitude,
        1000, // 1km radius
        'clients'
      );

      if (result.success && result.results) {
        setNearbyClients(result.results);
        setIsNearbyModalOpen(true);
      }
    } catch (error) {
      console.error('Error finding nearby clients:', error);
    }
  };

  const handleGetCurrentLocation = async () => {
    try {
      const position = await getCurrentPosition();
      const location = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude
      };
      setCurrentLocation(location);
    } catch (error) {
      console.error('Error getting current location:', error);
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Geolocation & Offline Settings</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage location services and offline data synchronization
          </p>
        </div>

        {/* Network Status Card */}
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-gray-900">Network Status</h2>
            <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm ${
              isOnline 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            }`}>
              <div className={`w-2 h-2 rounded-full mr-2 ${
                isOnline ? 'bg-green-500' : 'bg-red-500'
              }`}></div>
              {isOnline ? 'Online' : 'Offline'}
            </div>
          </div>
          
          {!isOnline && (
            <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
              <p className="text-sm text-yellow-800">
                You are currently offline. Changes will be synchronized when connection is restored.
              </p>
            </div>
          )}
        </div>

        {/* Geolocation Card */}
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-gray-900">Location Services</h2>
            <Button
              onClick={handleGetCurrentLocation}
              className="flex items-center space-x-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span>Get Current Location</span>
            </Button>
          </div>

          <LocationPicker
            initialLocation={currentLocation}
            onLocationChange={handleLocationChange}
          />

          {currentLocation && (
            <div className="mt-4 flex space-x-2">
              <Button
                onClick={handleFindNearby}
                className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <span>Find Nearby Clients</span>
              </Button>
            </div>
          )}
        </div>

        {/* Offline Management Card */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Offline Data Management</h2>
          
          {offlineDataAge && (
            <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded">
              <p className="text-sm text-blue-800">
                Offline data last updated: {offlineDataAge}
              </p>
            </div>
          )}

          <OfflineManager />
        </div>

        {/* Nearby Clients Modal */}
        <Modal
          isOpen={isNearbyModalOpen}
          onClose={() => setIsNearbyModalOpen(false)}
          title="Nearby Clients"
        >
          <div className="space-y-4">
            {nearbyClients.length > 0 ? (
              <div className="space-y-3">
                <p className="text-sm text-gray-600">
                  Found {nearbyClients.length} client(s) within 1km:
                </p>
                {nearbyClients.map((client) => (
                  <div key={client.id} className="border rounded p-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium text-gray-900">{client.name}</h4>
                        <p className="text-sm text-gray-600">{client.address}</p>
                        <p className="text-sm text-gray-500">{client.city}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium text-blue-600">
                          {client.distance ? `${(client.distance / 1000).toFixed(1)} km` : 'N/A'}
                        </div>
                        <div className="text-xs text-gray-500">
                          {client.client_type}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No clients found nearby.</p>
            )}
          </div>
        </Modal>
      </div>
    </Layout>
  );
};
