import React, { useState, useEffect } from 'react';
import { LocationPicker } from '../Geolocation/LocationPicker';
import { LocationTracker } from '../Geolocation/LocationTracker';
import { Button } from '../UI/Button';
import { Modal } from '../UI/Modal';
import { 
  findNearby, 
  getCurrentPosition, 
  Location,
  OfflineStorageManager 
} from '../../services';

interface InspectionLocationProps {
  inspectionId: number;
  initialLocation?: Location;
  onLocationChange?: (location: Location) => void;
  onTrackingData?: (data: any) => void;
  isOffline?: boolean;
}

export const InspectionLocation: React.FC<InspectionLocationProps> = ({
  inspectionId,
  initialLocation,
  onLocationChange,
  onTrackingData,
  isOffline = false
}) => {
  const [currentLocation, setCurrentLocation] = useState<Location | null>(initialLocation || null);
  const [isTracking, setIsTracking] = useState(false);
  const [showNearbyModal, setShowNearbyModal] = useState(false);
  const [nearbyItems, setNearbyItems] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (initialLocation) {
      setCurrentLocation(initialLocation);
    }
  }, [initialLocation]);

  const handleLocationChange = (location: Location) => {
    setCurrentLocation(location);
    onLocationChange?.(location);
    
    // Store location offline if needed
    if (isOffline) {
      OfflineStorageManager.storeData({
        inspection_location: {
          inspection_id: inspectionId,
          location: location,
          timestamp: new Date().toISOString()
        }
      });
    }
  };

  const handleGetCurrentLocation = async () => {
    try {
      setIsLoading(true);
      setError('');
      
      const position = await getCurrentPosition();
      const location = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude
      };
      
      setCurrentLocation(location);
      handleLocationChange(location);
    } catch (error: any) {
      setError(`Erreur lors de la récupération de la position: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFindNearby = async () => {
    if (!currentLocation) return;

    try {
      setIsLoading(true);
      setError('');

      // Find nearby clients
      const clientsResult = await findNearby(
        currentLocation.latitude,
        currentLocation.longitude,
        1000, // 1km radius
        'clients'
      );

      // Find nearby interventions
      const interventionsResult = await findNearby(
        currentLocation.latitude,
        currentLocation.longitude,
        1000,
        'interventions'
      );

      const nearby = [
        ...(clientsResult.results || []).map(item => ({ ...item, type: 'client' })),
        ...(interventionsResult.results || []).map(item => ({ ...item, type: 'intervention' }))
      ];

      setNearbyItems(nearby);
      setShowNearbyModal(true);
    } catch (error: any) {
      setError('Erreur lors de la recherche de proximité');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTrackingStart = () => {
    setIsTracking(true);
  };

  const handleTrackingStop = (trackingData: any) => {
    setIsTracking(false);
    onTrackingData?.(trackingData);
  };

  const handleLocationRecord = (location: any) => {
    // Store tracking data offline if needed
    if (isOffline) {
      const trackingData = OfflineStorageManager.getData()?.tracking_data || [];
      trackingData.push({
        inspection_id: inspectionId,
        location: location,
        timestamp: new Date().toISOString()
      });
      
      OfflineStorageManager.storeData({
        ...OfflineStorageManager.getData(),
        tracking_data: trackingData
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* Location Picker */}
      <div className="bg-white border rounded-lg p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Localisation de l'inspection</h3>
          <div className="flex space-x-2">
            <Button
              onClick={handleGetCurrentLocation}
              disabled={isLoading}
              className="flex items-center space-x-2"
            >
              {isLoading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              )}
              <span>Position actuelle</span>
            </Button>
            
            {currentLocation && (
              <Button
                onClick={handleFindNearby}
                disabled={isLoading}
                className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <span>Proximité</span>
              </Button>
            )}
          </div>
        </div>

        <LocationPicker
          initialLocation={currentLocation}
          onLocationChange={handleLocationChange}
          showAddressInput={true}
        />

        {error && (
          <div className="mt-4 bg-red-50 border border-red-200 rounded p-3">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}
      </div>

      {/* Location Tracking */}
      <div className="bg-white border rounded-lg p-4">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Suivi de position</h3>
        
        <LocationTracker
          inspectionId={inspectionId}
          onTrackingStart={handleTrackingStart}
          onTrackingStop={handleTrackingStop}
          onLocationRecord={handleLocationRecord}
          autoRecord={true}
          recordInterval={30}
        />
      </div>

      {/* Offline Status */}
      {isOffline && (
        <div className="bg-yellow-50 border border-yellow-200 rounded p-4">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-yellow-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <p className="text-sm text-yellow-800">
              Mode hors-ligne activé. Les données de localisation seront synchronisées lors de la reconnexion.
            </p>
          </div>
        </div>
      )}

      {/* Nearby Items Modal */}
      <Modal
        isOpen={showNearbyModal}
        onClose={() => setShowNearbyModal(false)}
        title="Éléments à proximité"
      >
        <div className="space-y-4">
          {nearbyItems.length > 0 ? (
            <div className="space-y-3">
              <p className="text-sm text-gray-600">
                {nearbyItems.length} élément(s) trouvé(s) dans un rayon de 1km:
              </p>
              
              <div className="max-h-96 overflow-y-auto space-y-2">
                {nearbyItems.map((item, index) => (
                  <div key={index} className="border rounded p-3 hover:bg-gray-50">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <span className={`px-2 py-1 text-xs rounded ${
                            item.type === 'client' 
                              ? 'bg-blue-100 text-blue-800' 
                              : 'bg-green-100 text-green-800'
                          }`}>
                            {item.type === 'client' ? 'Client' : 'Intervention'}
                          </span>
                          <h4 className="font-medium text-gray-900">{item.name}</h4>
                        </div>
                        
                        {item.address && (
                          <p className="text-sm text-gray-600 mt-1">{item.address}</p>
                        )}
                        
                        {item.city && (
                          <p className="text-sm text-gray-500">{item.city}</p>
                        )}
                        
                        {item.title && (
                          <p className="text-sm text-gray-600 mt-1">{item.title}</p>
                        )}
                        
                        {item.status && (
                          <span className={`inline-block px-2 py-1 text-xs rounded mt-1 ${
                            item.status === 'completed' 
                              ? 'bg-green-100 text-green-800'
                              : item.status === 'in_progress'
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}>
                            {item.status}
                          </span>
                        )}
                      </div>
                      
                      <div className="text-right">
                        {item.distance && (
                          <div className="text-sm font-medium text-blue-600">
                            {Math.round(item.distance / 1000 * 10) / 10} km
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">
              Aucun élément trouvé à proximité.
            </p>
          )}
        </div>
      </Modal>
    </div>
  );
};
