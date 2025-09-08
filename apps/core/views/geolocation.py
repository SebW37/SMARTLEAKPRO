"""
Geolocation views for SmartLeakPro application.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
# # from django.contrib.gis.geos import Point
from apps.core.services.geolocation import geolocation_service, location_tracker
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def geocode_address(request):
    """
    Geocode an address to get coordinates.
    
    POST /api/geolocation/geocode/
    {
        "address": "123 Rue de la Paix, 75001 Paris, France"
    }
    """
    try:
        address = request.data.get('address')
        if not address:
            return Response(
                {'error': 'Address is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        location = geolocation_service.geocode_address(address)
        
        if location:
            return Response({
                'success': True,
                'location': {
                    'latitude': location.y,
                    'longitude': location.x
                },
                'address': address
            })
        else:
            return Response(
                {'error': 'Unable to geocode address'},
                status=status.HTTP_404_NOT_FOUND
            )
            
    except Exception as e:
        logger.error(f"Geocoding error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reverse_geocode(request):
    """
    Reverse geocode coordinates to get address.
    
    POST /api/geolocation/reverse/
    {
        "latitude": 48.8566,
        "longitude": 2.3522
    }
    """
    try:
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        
        if latitude is None or longitude is None:
            return Response(
                {'error': 'Latitude and longitude are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate coordinates
        if not geolocation_service.validate_coordinates(latitude, longitude):
            return Response(
                {'error': 'Invalid coordinates'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        address_info = geolocation_service.reverse_geocode(latitude, longitude)
        
        if address_info:
            return Response({
                'success': True,
                'address': address_info,
                'coordinates': {
                    'latitude': latitude,
                    'longitude': longitude
                }
            })
        else:
            return Response(
                {'error': 'Unable to reverse geocode coordinates'},
                status=status.HTTP_404_NOT_FOUND
            )
            
    except Exception as e:
        logger.error(f"Reverse geocoding error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_distance(request):
    """
    Calculate distance between two points.
    
    POST /api/geolocation/distance/
    {
        "point1": {"latitude": 48.8566, "longitude": 2.3522},
        "point2": {"latitude": 48.8606, "longitude": 2.3376}
    }
    """
    try:
        point1_data = request.data.get('point1')
        point2_data = request.data.get('point2')
        
        if not point1_data or not point2_data:
            return Response(
                {'error': 'Both points are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate and create points
        lat1, lng1 = point1_data.get('latitude'), point1_data.get('longitude')
        lat2, lng2 = point2_data.get('latitude'), point2_data.get('longitude')
        
        if any(coord is None for coord in [lat1, lng1, lat2, lng2]):
            return Response(
                {'error': 'Invalid point coordinates'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not all(geolocation_service.validate_coordinates(lat, lng) 
                  for lat, lng in [(lat1, lng1), (lat2, lng2)]):
            return Response(
                {'error': 'Invalid coordinates'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        point1 = # Point(lng1, lat1)
        point2 = # Point(lng2, lat2)
        
        distance_meters = geolocation_service.calculate_distance(point1, point2)
        
        return Response({
            'success': True,
            'distance': {
                'meters': round(distance_meters, 2),
                'kilometers': round(distance_meters / 1000, 2),
                'miles': round(distance_meters / 1609.34, 2)
            },
            'points': {
                'point1': point1_data,
                'point2': point2_data
            }
        })
        
    except Exception as e:
        logger.error(f"Distance calculation error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def find_nearby(request):
    """
    Find nearby locations.
    
    POST /api/geolocation/nearby/
    {
        "latitude": 48.8566,
        "longitude": 2.3522,
        "radius": 1000,
        "type": "clients"
    }
    """
    try:
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        radius = request.data.get('radius', 1000)  # Default 1km
        location_type = request.data.get('type', 'clients')
        
        if latitude is None or longitude is None:
            return Response(
                {'error': 'Latitude and longitude are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not geolocation_service.validate_coordinates(latitude, longitude):
            return Response(
                {'error': 'Invalid coordinates'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        center_point = # Point(longitude, latitude)
        
        # Get model class based on type
        if location_type == 'clients':
            from apps.clients.models import Client
            model_class = Client
        elif location_type == 'client_sites':
            from apps.clients.models import ClientSite
            model_class = ClientSite
        elif location_type == 'interventions':
            from apps.interventions.models import Intervention
            model_class = Intervention
        elif location_type == 'inspections':
            from apps.inspections.models import Inspection
            model_class = Inspection
        else:
            return Response(
                {'error': 'Invalid location type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        nearby_objects = geolocation_service.find_nearby_locations(
            center_point, radius, model_class
        )
        
        # Serialize results
        results = []
        for obj in nearby_objects:
            if hasattr(obj, 'location') and obj.location:
                result = {
                    'id': obj.id,
                    'name': getattr(obj, 'name', str(obj)),
                    'location': {
                        'latitude': obj.location.y,
                        'longitude': obj.location.x
                    },
                    'distance': getattr(obj, 'distance', None)
                }
                
                # Add type-specific fields
                if location_type == 'clients':
                    result.update({
                        'client_type': obj.client_type,
                        'address': obj.address,
                        'city': obj.city
                    })
                elif location_type == 'interventions':
                    result.update({
                        'title': obj.title,
                        'status': obj.status,
                        'priority': obj.priority,
                        'scheduled_date': obj.scheduled_date.isoformat() if obj.scheduled_date else None
                    })
                
                results.append(result)
        
        return Response({
            'success': True,
            'center': {
                'latitude': latitude,
                'longitude': longitude
            },
            'radius': radius,
            'type': location_type,
            'count': len(results),
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Nearby search error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_location_tracking(request):
    """
    Start location tracking for an inspection.
    
    POST /api/geolocation/tracking/start/
    {
        "inspection_id": 123
    }
    """
    try:
        inspection_id = request.data.get('inspection_id')
        if not inspection_id:
            return Response(
                {'error': 'Inspection ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success = location_tracker.start_tracking(request.user.id, inspection_id)
        
        if success:
            return Response({
                'success': True,
                'message': 'Location tracking started',
                'inspection_id': inspection_id
            })
        else:
            return Response(
                {'error': 'Failed to start location tracking'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"Start tracking error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def record_location(request):
    """
    Record a location point during tracking.
    
    POST /api/geolocation/tracking/record/
    {
        "inspection_id": 123,
        "latitude": 48.8566,
        "longitude": 2.3522,
        "accuracy": 5.0
    }
    """
    try:
        inspection_id = request.data.get('inspection_id')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        accuracy = request.data.get('accuracy')
        
        if not all([inspection_id, latitude is not None, longitude is not None]):
            return Response(
                {'error': 'Inspection ID, latitude, and longitude are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not geolocation_service.validate_coordinates(latitude, longitude):
            return Response(
                {'error': 'Invalid coordinates'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success = location_tracker.record_location(
            request.user.id, inspection_id, latitude, longitude, accuracy
        )
        
        if success:
            return Response({
                'success': True,
                'message': 'Location recorded',
                'location': {
                    'latitude': latitude,
                    'longitude': longitude,
                    'accuracy': accuracy
                }
            })
        else:
            return Response(
                {'error': 'Failed to record location'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"Record location error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_location_tracking(request):
    """
    Stop location tracking for an inspection.
    
    POST /api/geolocation/tracking/stop/
    {
        "inspection_id": 123
    }
    """
    try:
        inspection_id = request.data.get('inspection_id')
        if not inspection_id:
            return Response(
                {'error': 'Inspection ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tracking_data = location_tracker.stop_tracking(request.user.id, inspection_id)
        
        if tracking_data:
            return Response({
                'success': True,
                'message': 'Location tracking stopped',
                'tracking_data': tracking_data
            })
        else:
            return Response(
                {'error': 'No active tracking found'},
                status=status.HTTP_404_NOT_FOUND
            )
            
    except Exception as e:
        logger.error(f"Stop tracking error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tracking_status(request, inspection_id):
    """
    Get location tracking status for an inspection.
    
    GET /api/geolocation/tracking/status/{inspection_id}/
    """
    try:
        tracking_data = location_tracker.get_tracking_status(request.user.id, inspection_id)
        
        if tracking_data:
            return Response({
                'success': True,
                'tracking': True,
                'tracking_data': tracking_data
            })
        else:
            return Response({
                'success': True,
                'tracking': False,
                'message': 'No active tracking'
            })
            
    except Exception as e:
        logger.error(f"Get tracking status error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
