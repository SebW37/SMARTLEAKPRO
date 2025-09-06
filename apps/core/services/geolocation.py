"""
Geolocation services for SmartLeakPro application.
"""
import requests
import logging
from typing import Optional, Tuple, Dict, Any
from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)


class GeolocationService:
    """Service for handling geolocation operations."""
    
    def __init__(self):
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.reverse_url = "https://nominatim.openstreetmap.org/reverse"
        
    def geocode_address(self, address: str) -> Optional[Point]:
        """
        Convert an address to geographic coordinates using OpenStreetMap Nominatim.
        
        Args:
            address (str): The address to geocode
            
        Returns:
            Point or None: Geographic point or None if geocoding fails
        """
        if not address:
            return None
            
        # Check cache first
        cache_key = f"geocode:{address}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return Point(cached_result['lon'], cached_result['lat'])
        
        try:
            params = {
                'q': address,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1
            }
            
            headers = {
                'User-Agent': 'SmartLeakPro/1.0 (contact@smartleakpro.com)'
            }
            
            response = requests.get(
                self.nominatim_url,
                params=params,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            if data:
                location_data = data[0]
                lat = float(location_data['lat'])
                lon = float(location_data['lon'])
                
                # Cache the result for 24 hours
                cache.set(cache_key, {'lat': lat, 'lon': lon}, 86400)
                
                return Point(lon, lat)
                
        except Exception as e:
            logger.error(f"Geocoding failed for address '{address}': {str(e)}")
            
        return None
    
    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """
        Convert geographic coordinates to an address.
        
        Args:
            latitude (float): Latitude coordinate
            longitude (float): Longitude coordinate
            
        Returns:
            dict or None: Address information or None if reverse geocoding fails
        """
        # Check cache first
        cache_key = f"reverse_geocode:{latitude}:{longitude}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            params = {
                'lat': latitude,
                'lon': longitude,
                'format': 'json',
                'addressdetails': 1
            }
            
            headers = {
                'User-Agent': 'SmartLeakPro/1.0 (contact@smartleakpro.com)'
            }
            
            response = requests.get(
                self.reverse_url,
                params=params,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            if data and 'address' in data:
                address_info = {
                    'display_name': data.get('display_name', ''),
                    'house_number': data['address'].get('house_number', ''),
                    'road': data['address'].get('road', ''),
                    'city': data['address'].get('city') or data['address'].get('town') or data['address'].get('village', ''),
                    'postcode': data['address'].get('postcode', ''),
                    'country': data['address'].get('country', ''),
                    'country_code': data['address'].get('country_code', ''),
                }
                
                # Cache the result for 24 hours
                cache.set(cache_key, address_info, 86400)
                
                return address_info
                
        except Exception as e:
            logger.error(f"Reverse geocoding failed for coordinates {latitude}, {longitude}: {str(e)}")
            
        return None
    
    def calculate_distance(self, point1: Point, point2: Point) -> float:
        """
        Calculate distance between two points in meters.
        
        Args:
            point1 (Point): First geographic point
            point2 (Point): Second geographic point
            
        Returns:
            float: Distance in meters
        """
        try:
            # Transform to a projected coordinate system for accurate distance calculation
            point1_transformed = point1.transform(3857, clone=True)  # Web Mercator
            point2_transformed = point2.transform(3857, clone=True)
            
            return point1_transformed.distance(point2_transformed)
        except Exception as e:
            logger.error(f"Distance calculation failed: {str(e)}")
            return 0.0
    
    def find_nearby_locations(self, center_point: Point, radius_meters: float, 
                             model_class, location_field: str = 'location') -> list:
        """
        Find locations within a specified radius of a center point.
        
        Args:
            center_point (Point): Center point for search
            radius_meters (float): Search radius in meters
            model_class: Django model class to search
            location_field (str): Name of the location field in the model
            
        Returns:
            list: List of nearby objects
        """
        try:
            from django.contrib.gis.measure import D
            from django.contrib.gis.db.models.functions import Distance
            
            filter_kwargs = {
                f'{location_field}__distance_lte': (center_point, D(m=radius_meters))
            }
            
            nearby_objects = model_class.objects.filter(**filter_kwargs).annotate(
                distance=Distance(location_field, center_point)
            ).order_by('distance')
            
            return list(nearby_objects)
            
        except Exception as e:
            logger.error(f"Nearby search failed: {str(e)}")
            return []
    
    def validate_coordinates(self, latitude: float, longitude: float) -> bool:
        """
        Validate geographic coordinates.
        
        Args:
            latitude (float): Latitude coordinate
            longitude (float): Longitude coordinate
            
        Returns:
            bool: True if coordinates are valid
        """
        return (-90 <= latitude <= 90) and (-180 <= longitude <= 180)
    
    def get_location_bounds(self, locations: list) -> Optional[Dict[str, float]]:
        """
        Calculate bounding box for a list of locations.
        
        Args:
            locations (list): List of Point objects
            
        Returns:
            dict: Bounding box with min/max lat/lng or None if no locations
        """
        if not locations:
            return None
            
        try:
            lats = [loc.y for loc in locations if loc]
            lngs = [loc.x for loc in locations if loc]
            
            if not lats or not lngs:
                return None
            
            return {
                'min_lat': min(lats),
                'max_lat': max(lats),
                'min_lng': min(lngs),
                'max_lng': max(lngs)
            }
            
        except Exception as e:
            logger.error(f"Bounds calculation failed: {str(e)}")
            return None


class LocationTracker:
    """Service for tracking user locations during inspections."""
    
    def __init__(self):
        self.redis_key_prefix = "location_track"
    
    def start_tracking(self, user_id: int, inspection_id: int) -> bool:
        """
        Start location tracking for a user during an inspection.
        
        Args:
            user_id (int): User ID
            inspection_id (int): Inspection ID
            
        Returns:
            bool: True if tracking started successfully
        """
        try:
            cache_key = f"{self.redis_key_prefix}:{user_id}:{inspection_id}"
            tracking_data = {
                'started_at': timezone.now().isoformat(),
                'user_id': user_id,
                'inspection_id': inspection_id,
                'locations': []
            }
            
            # Store tracking data for 24 hours
            cache.set(cache_key, tracking_data, 86400)
            return True
            
        except Exception as e:
            logger.error(f"Failed to start location tracking: {str(e)}")
            return False
    
    def record_location(self, user_id: int, inspection_id: int, 
                       latitude: float, longitude: float, 
                       accuracy: Optional[float] = None) -> bool:
        """
        Record a location point during tracking.
        
        Args:
            user_id (int): User ID
            inspection_id (int): Inspection ID
            latitude (float): Latitude coordinate
            longitude (float): Longitude coordinate
            accuracy (float, optional): GPS accuracy in meters
            
        Returns:
            bool: True if location recorded successfully
        """
        try:
            cache_key = f"{self.redis_key_prefix}:{user_id}:{inspection_id}"
            tracking_data = cache.get(cache_key)
            
            if not tracking_data:
                return False
            
            location_point = {
                'timestamp': timezone.now().isoformat(),
                'latitude': latitude,
                'longitude': longitude,
                'accuracy': accuracy
            }
            
            tracking_data['locations'].append(location_point)
            cache.set(cache_key, tracking_data, 86400)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to record location: {str(e)}")
            return False
    
    def stop_tracking(self, user_id: int, inspection_id: int) -> Optional[Dict[str, Any]]:
        """
        Stop location tracking and return the tracked data.
        
        Args:
            user_id (int): User ID
            inspection_id (int): Inspection ID
            
        Returns:
            dict or None: Tracking data or None if tracking not found
        """
        try:
            cache_key = f"{self.redis_key_prefix}:{user_id}:{inspection_id}"
            tracking_data = cache.get(cache_key)
            
            if tracking_data:
                tracking_data['stopped_at'] = timezone.now().isoformat()
                cache.delete(cache_key)
                return tracking_data
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to stop location tracking: {str(e)}")
            return None
    
    def get_tracking_status(self, user_id: int, inspection_id: int) -> Optional[Dict[str, Any]]:
        """
        Get current tracking status and data.
        
        Args:
            user_id (int): User ID
            inspection_id (int): Inspection ID
            
        Returns:
            dict or None: Current tracking data or None if not tracking
        """
        try:
            cache_key = f"{self.redis_key_prefix}:{user_id}:{inspection_id}"
            return cache.get(cache_key)
            
        except Exception as e:
            logger.error(f"Failed to get tracking status: {str(e)}")
            return None


# Service instances
geolocation_service = GeolocationService()
location_tracker = LocationTracker()
