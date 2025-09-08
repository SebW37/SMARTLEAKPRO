import React, { useState, useEffect } from 'react';
import { Button } from '../UI/Button';
import { Input } from '../UI/Input';
import { LoadingSpinner } from '../UI/LoadingSpinner';
import { geocodeAddress, reverseGeocode } from '../../services/geolocationService';

interface Location {
  latitude: number;
  longitude: number;
}

interface LocationPickerProps {
  initialLocation?: Location;
  onLocationChange: (location: Location) => void;
  showAddressInput?: boolean;
  className?: string;
}

export const LocationPicker: React.FC<LocationPickerProps> = ({
  initialLocation,
  onLocationChange,
  showAddressInput = true,
  className = ''
}) => {
  const [location, setLocation] = useState<Location | null>(initialLocation || null);
  const [address, setAddress] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isGeocodingAddress, setIsGeocodingAddress] = useState(false);

  useEffect(() => {
    if (initialLocation) {
      setLocation(initialLocation);
      // Reverse geocode to get address
      handleReverseGeocode(initialLocation);
    }
  }, [initialLocation]);

  const getCurrentLocation = () => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by this browser');
      return;
    }

    setIsLoading(true);
    setError('');

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const newLocation = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude
        };
        setLocation(newLocation);
        onLocationChange(newLocation);
        handleReverseGeocode(newLocation);
        setIsLoading(false);
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

  const handleReverseGeocode = async (loc: Location) => {
    try {
      const result = await reverseGeocode(loc.latitude, loc.longitude);
      if (result.success && result.address) {
        setAddress(result.address.display_name || '');
      }
    } catch (error) {
      console.error('Reverse geocoding failed:', error);
    }
  };

  const handleAddressGeocode = async () => {
    if (!address.trim()) return;

    setIsGeocodingAddress(true);
    setError('');

    try {
      const result = await geocodeAddress(address);
      if (result.success && result.location) {
        const newLocation = {
          latitude: result.location.latitude,
          longitude: result.location.longitude
        };
        setLocation(newLocation);
        onLocationChange(newLocation);
      } else {
        setError('Unable to find location for this address');
      }
    } catch (error) {
      setError('Error geocoding address');
    } finally {
      setIsGeocodingAddress(false);
    }
  };

  const handleManualCoordinates = (lat: string, lng: string) => {
    const latitude = parseFloat(lat);
    const longitude = parseFloat(lng);

    if (isNaN(latitude) || isNaN(longitude)) {
      setError('Invalid coordinates');
      return;
    }

    if (latitude < -90 || latitude > 90 || longitude < -180 || longitude > 180) {
      setError('Coordinates out of range');
      return;
    }

    const newLocation = { latitude, longitude };
    setLocation(newLocation);
    onLocationChange(newLocation);
    handleReverseGeocode(newLocation);
    setError('');
  };

  return (
    <div className={`space-y-4 ${className}`}>
      <div className="border rounded-lg p-4">
        <h3 className="text-lg font-medium mb-4">Location</h3>
        
        {/* Current Location Button */}
        <div className="flex items-center space-x-2 mb-4">
          <Button
            onClick={getCurrentLocation}
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
            <span>Use Current Location</span>
          </Button>
        </div>

        {/* Address Input */}
        {showAddressInput && (
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Address
            </label>
            <div className="flex space-x-2">
              <Input
                type="text"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                placeholder="Enter address to geocode"
                className="flex-1"
              />
              <Button
                onClick={handleAddressGeocode}
                disabled={isGeocodingAddress || !address.trim()}
              >
                {isGeocodingAddress ? <LoadingSpinner size="sm" /> : 'Geocode'}
              </Button>
            </div>
          </div>
        )}

        {/* Manual Coordinates */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Latitude
            </label>
            <Input
              type="number"
              step="any"
              value={location?.latitude || ''}
              onChange={(e) => handleManualCoordinates(e.target.value, location?.longitude?.toString() || '')}
              placeholder="Latitude"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Longitude
            </label>
            <Input
              type="number"
              step="any"
              value={location?.longitude || ''}
              onChange={(e) => handleManualCoordinates(location?.latitude?.toString() || '', e.target.value)}
              placeholder="Longitude"
            />
          </div>
        </div>

        {/* Current Location Display */}
        {location && (
          <div className="bg-green-50 border border-green-200 rounded p-3">
            <p className="text-sm text-green-800">
              <strong>Current Location:</strong><br />
              Latitude: {location.latitude.toFixed(6)}<br />
              Longitude: {location.longitude.toFixed(6)}
            </p>
            {address && (
              <p className="text-sm text-green-800 mt-2">
                <strong>Address:</strong> {address}
              </p>
            )}
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
