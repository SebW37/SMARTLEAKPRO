import { api } from './api';

export interface Location {
  latitude: number;
  longitude: number;
}

export interface GeocodeResult {
  success: boolean;
  location?: Location;
  address?: string;
  error?: string;
}

export interface ReverseGeocodeResult {
  success: boolean;
  address?: {
    display_name: string;
    house_number: string;
    road: string;
    city: string;
    postcode: string;
    country: string;
    country_code: string;
  };
  coordinates?: Location;
  error?: string;
}

export interface DistanceResult {
  success: boolean;
  distance?: {
    meters: number;
    kilometers: number;
    miles: number;
  };
  points?: {
    point1: Location;
    point2: Location;
  };
  error?: string;
}

export interface NearbyResult {
  success: boolean;
  center?: Location;
  radius?: number;
  type?: string;
  count?: number;
  results?: Array<{
    id: number;
    name: string;
    location: Location;
    distance?: number;
    [key: string]: any;
  }>;
  error?: string;
}

export interface TrackingResult {
  success: boolean;
  message?: string;
  inspection_id?: number;
  tracking_data?: any;
  location?: Location & { accuracy?: number };
  error?: string;
}

export interface TrackingStatusResult {
  success: boolean;
  tracking: boolean;
  tracking_data?: any;
  message?: string;
  error?: string;
}

// Geocoding functions
export const geocodeAddress = async (address: string): Promise<GeocodeResult> => {
  try {
    const response = await api.post('/core/geolocation/geocode/', { address });
    return response.data;
  } catch (error: any) {
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to geocode address'
    };
  }
};

export const reverseGeocode = async (latitude: number, longitude: number): Promise<ReverseGeocodeResult> => {
  try {
    const response = await api.post('/core/geolocation/reverse/', {
      latitude,
      longitude
    });
    return response.data;
  } catch (error: any) {
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to reverse geocode coordinates'
    };
  }
};

export const calculateDistance = async (point1: Location, point2: Location): Promise<DistanceResult> => {
  try {
    const response = await api.post('/core/geolocation/distance/', {
      point1,
      point2
    });
    return response.data;
  } catch (error: any) {
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to calculate distance'
    };
  }
};

export const findNearby = async (
  latitude: number,
  longitude: number,
  radius: number = 1000,
  type: string = 'clients'
): Promise<NearbyResult> => {
  try {
    const response = await api.post('/core/geolocation/nearby/', {
      latitude,
      longitude,
      radius,
      type
    });
    return response.data;
  } catch (error: any) {
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to find nearby locations'
    };
  }
};

// Location tracking functions
export const startLocationTracking = async (inspectionId: number): Promise<TrackingResult> => {
  try {
    const response = await api.post('/core/geolocation/tracking/start/', {
      inspection_id: inspectionId
    });
    return response.data;
  } catch (error: any) {
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to start location tracking'
    };
  }
};

export const recordLocation = async (
  inspectionId: number,
  latitude: number,
  longitude: number,
  accuracy?: number
): Promise<TrackingResult> => {
  try {
    const response = await api.post('/core/geolocation/tracking/record/', {
      inspection_id: inspectionId,
      latitude,
      longitude,
      accuracy
    });
    return response.data;
  } catch (error: any) {
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to record location'
    };
  }
};

export const stopLocationTracking = async (inspectionId: number): Promise<TrackingResult> => {
  try {
    const response = await api.post('/core/geolocation/tracking/stop/', {
      inspection_id: inspectionId
    });
    return response.data;
  } catch (error: any) {
    return {
      success: false,
      error: error.response?.data?.error || 'Failed to stop location tracking'
    };
  }
};

export const getTrackingStatus = async (inspectionId: number): Promise<TrackingStatusResult> => {
  try {
    const response = await api.get(`/core/geolocation/tracking/status/${inspectionId}/`);
    return response.data;
  } catch (error: any) {
    return {
      success: false,
      tracking: false,
      error: error.response?.data?.error || 'Failed to get tracking status'
    };
  }
};

// Utility functions
export const validateCoordinates = (latitude: number, longitude: number): boolean => {
  return (
    latitude >= -90 && latitude <= 90 &&
    longitude >= -180 && longitude <= 180
  );
};

export const formatCoordinates = (latitude: number, longitude: number, precision: number = 6): string => {
  return `${latitude.toFixed(precision)}, ${longitude.toFixed(precision)}`;
};

export const getCurrentPosition = (): Promise<GeolocationPosition> => {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation is not supported by this browser'));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => resolve(position),
      (error) => reject(error),
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000
      }
    );
  });
};

export const watchPosition = (
  onSuccess: (position: GeolocationPosition) => void,
  onError: (error: GeolocationPositionError) => void,
  options?: PositionOptions
): number => {
  if (!navigator.geolocation) {
    throw new Error('Geolocation is not supported by this browser');
  }

  return navigator.geolocation.watchPosition(
    onSuccess,
    onError,
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 5000,
      ...options
    }
  );
};

export const clearWatch = (watchId: number): void => {
  if (navigator.geolocation) {
    navigator.geolocation.clearWatch(watchId);
  }
};

// Distance calculation helpers
export const haversineDistance = (lat1: number, lon1: number, lat2: number, lon2: number): number => {
  const R = 6371e3; // Earth's radius in meters
  const φ1 = lat1 * Math.PI / 180;
  const φ2 = lat2 * Math.PI / 180;
  const Δφ = (lat2 - lat1) * Math.PI / 180;
  const Δλ = (lon2 - lon1) * Math.PI / 180;

  const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
            Math.cos(φ1) * Math.cos(φ2) *
            Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  return R * c; // Distance in meters
};

export const formatDistance = (meters: number): string => {
  if (meters < 1000) {
    return `${Math.round(meters)} m`;
  } else {
    return `${(meters / 1000).toFixed(1)} km`;
  }
};

// Location utilities for offline use
export const storeLocationOffline = (key: string, location: Location): void => {
  try {
    const locations = getStoredLocations();
    locations[key] = {
      ...location,
      timestamp: new Date().toISOString()
    };
    localStorage.setItem('offlineLocations', JSON.stringify(locations));
  } catch (error) {
    console.error('Failed to store location offline:', error);
  }
};

export const getStoredLocations = (): Record<string, Location & { timestamp: string }> => {
  try {
    const stored = localStorage.getItem('offlineLocations');
    return stored ? JSON.parse(stored) : {};
  } catch (error) {
    console.error('Failed to get stored locations:', error);
    return {};
  }
};

export const removeStoredLocation = (key: string): void => {
  try {
    const locations = getStoredLocations();
    delete locations[key];
    localStorage.setItem('offlineLocations', JSON.stringify(locations));
  } catch (error) {
    console.error('Failed to remove stored location:', error);
  }
};

export const clearStoredLocations = (): void => {
  try {
    localStorage.removeItem('offlineLocations');
  } catch (error) {
    console.error('Failed to clear stored locations:', error);
  }
};
