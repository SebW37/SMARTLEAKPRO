import React, { useState, useEffect, useRef } from 'react';
import { Button } from '../UI/Button';
import { LoadingSpinner } from '../UI/LoadingSpinner';
import { 
  startLocationTracking, 
  recordLocation, 
  stopLocationTracking, 
  getTrackingStatus 
} from '../../services/geolocationService';

interface LocationPoint {
  timestamp: string;
  latitude: number;
  longitude: number;
  accuracy?: number;
}

interface LocationTrackerProps {
  inspectionId: number;
  onTrackingStart?: () => void;
  onTrackingStop?: (trackingData: any) => void;
  onLocationRecord?: (location: LocationPoint) => void;
  autoRecord?: boolean;
  recordInterval?: number; // in seconds
}

export const LocationTracker: React.FC<LocationTrackerProps> = ({
  inspectionId,
  onTrackingStart,
  onTrackingStop,
  onLocationRecord,
  autoRecord = true,
  recordInterval = 30
}) => {
  const [isTracking, setIsTracking] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentLocation, setCurrentLocation] = useState<LocationPoint | null>(null);
  const [trackingData, setTrackingData] = useState<any>(null);
  const [recordedPoints, setRecordedPoints] = useState<LocationPoint[]>([]);

  const trackingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const watchIdRef = useRef<number | null>(null);

  useEffect(() => {
    // Check if tracking is already active
    checkTrackingStatus();
    
    return () => {
      if (watchIdRef.current !== null) {
        navigator.geolocation.clearWatch(watchIdRef.current);
      }
      if (trackingIntervalRef.current) {
        clearInterval(trackingIntervalRef.current);
      }
    };
  }, [inspectionId]);

  const checkTrackingStatus = async () => {
    try {
      const status = await getTrackingStatus(inspectionId);
      if (status.tracking) {
        setIsTracking(true);
        setTrackingData(status.tracking_data);
        if (autoRecord) {
          startLocationWatch();
        }
      }
    } catch (error) {
      console.error('Error checking tracking status:', error);
    }
  };

  const handleStartTracking = async () => {
    setIsLoading(true);
    setError('');

    try {
      const result = await startLocationTracking(inspectionId);
      if (result.success) {
        setIsTracking(true);
        onTrackingStart?.();
        
        if (autoRecord) {
          startLocationWatch();
        }
      } else {
        setError('Failed to start location tracking');
      }
    } catch (error) {
      setError('Error starting location tracking');
    } finally {
      setIsLoading(false);
    }
  };

  const handleStopTracking = async () => {
    setIsLoading(true);
    setError('');

    try {
      // Stop location watch
      if (watchIdRef.current !== null) {
        navigator.geolocation.clearWatch(watchIdRef.current);
        watchIdRef.current = null;
      }
      if (trackingIntervalRef.current) {
        clearInterval(trackingIntervalRef.current);
        trackingIntervalRef.current = null;
      }

      const result = await stopLocationTracking(inspectionId);
      if (result.success) {
        setIsTracking(false);
        setTrackingData(result.tracking_data);
        onTrackingStop?.(result.tracking_data);
      } else {
        setError('Failed to stop location tracking');
      }
    } catch (error) {
      setError('Error stopping location tracking');
    } finally {
      setIsLoading(false);
    }
  };

  const startLocationWatch = () => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by this browser');
      return;
    }

    watchIdRef.current = navigator.geolocation.watchPosition(
      (position) => {
        const locationPoint: LocationPoint = {
          timestamp: new Date().toISOString(),
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy
        };

        setCurrentLocation(locationPoint);
        setRecordedPoints(prev => [...prev, locationPoint]);
        onLocationRecord?.(locationPoint);

        // Record location on server if auto-recording
        if (autoRecord) {
          recordLocationOnServer(locationPoint);
        }
      },
      (error) => {
        setError(`Geolocation error: ${error.message}`);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 5000
      }
    );

    // Set up interval for recording
    if (autoRecord && recordInterval > 0) {
      trackingIntervalRef.current = setInterval(() => {
        if (currentLocation) {
          recordLocationOnServer(currentLocation);
        }
      }, recordInterval * 1000);
    }
  };

  const recordLocationOnServer = async (locationPoint: LocationPoint) => {
    try {
      await recordLocation(
        inspectionId,
        locationPoint.latitude,
        locationPoint.longitude,
        locationPoint.accuracy
      );
    } catch (error) {
      console.error('Error recording location on server:', error);
    }
  };

  const handleRecordCurrentLocation = async () => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by this browser');
      return;
    }

    setIsLoading(true);

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const locationPoint: LocationPoint = {
          timestamp: new Date().toISOString(),
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy
        };

        try {
          const result = await recordLocation(
            inspectionId,
            locationPoint.latitude,
            locationPoint.longitude,
            locationPoint.accuracy
          );

          if (result.success) {
            setCurrentLocation(locationPoint);
            setRecordedPoints(prev => [...prev, locationPoint]);
            onLocationRecord?.(locationPoint);
          } else {
            setError('Failed to record location');
          }
        } catch (error) {
          setError('Error recording location');
        } finally {
          setIsLoading(false);
        }
      },
      (error) => {
        setError(`Error getting location: ${error.message}`);
        setIsLoading(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000
      }
    );
  };

  return (
    <div className="space-y-4">
      <div className="border rounded-lg p-4">
        <h3 className="text-lg font-medium mb-4">Location Tracking</h3>
        
        {/* Tracking Controls */}
        <div className="flex items-center space-x-2 mb-4">
          {!isTracking ? (
            <Button
              onClick={handleStartTracking}
              disabled={isLoading}
              className="flex items-center space-x-2 bg-green-600 hover:bg-green-700"
            >
              {isLoading ? (
                <LoadingSpinner size="sm" />
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1M13 16h-1v-1a1 1 0 00-1-1H9a1 1 0 00-1 1v1H7" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              )}
              <span>Start Tracking</span>
            </Button>
          ) : (
            <Button
              onClick={handleStopTracking}
              disabled={isLoading}
              className="flex items-center space-x-2 bg-red-600 hover:bg-red-700"
            >
              {isLoading ? (
                <LoadingSpinner size="sm" />
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 9l6 6m0-6l-6 6" />
                </svg>
              )}
              <span>Stop Tracking</span>
            </Button>
          )}

          {isTracking && !autoRecord && (
            <Button
              onClick={handleRecordCurrentLocation}
              disabled={isLoading}
              className="flex items-center space-x-2"
            >
              {isLoading ? (
                <LoadingSpinner size="sm" />
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              )}
              <span>Record Location</span>
            </Button>
          )}
        </div>

        {/* Tracking Status */}
        <div className="mb-4">
          <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm ${
            isTracking 
              ? 'bg-green-100 text-green-800' 
              : 'bg-gray-100 text-gray-800'
          }`}>
            <div className={`w-2 h-2 rounded-full mr-2 ${
              isTracking ? 'bg-green-500' : 'bg-gray-500'
            }`}></div>
            {isTracking ? 'Tracking Active' : 'Tracking Inactive'}
          </div>
          
          {autoRecord && isTracking && (
            <p className="text-sm text-gray-600 mt-2">
              Auto-recording every {recordInterval} seconds
            </p>
          )}
        </div>

        {/* Current Location */}
        {currentLocation && (
          <div className="bg-blue-50 border border-blue-200 rounded p-3 mb-4">
            <h4 className="font-medium text-blue-900 mb-2">Current Location</h4>
            <p className="text-sm text-blue-800">
              Latitude: {currentLocation.latitude.toFixed(6)}<br />
              Longitude: {currentLocation.longitude.toFixed(6)}<br />
              {currentLocation.accuracy && (
                <>Accuracy: ±{Math.round(currentLocation.accuracy)} meters<br /></>
              )}
              Time: {new Date(currentLocation.timestamp).toLocaleString()}
            </p>
          </div>
        )}

        {/* Recorded Points Summary */}
        {recordedPoints.length > 0 && (
          <div className="bg-gray-50 border border-gray-200 rounded p-3 mb-4">
            <h4 className="font-medium text-gray-900 mb-2">Tracking Summary</h4>
            <p className="text-sm text-gray-600">
              Recorded points: {recordedPoints.length}<br />
              First point: {new Date(recordedPoints[0].timestamp).toLocaleString()}<br />
              Last point: {new Date(recordedPoints[recordedPoints.length - 1].timestamp).toLocaleString()}
            </p>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded p-3">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}
      </div>
    </div>
  );
};
