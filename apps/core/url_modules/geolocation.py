"""
Geolocation URLs for SmartLeakPro application.
"""
from django.urls import path
from apps.core.views.geolocation import (
    geocode_address,
    reverse_geocode,
    calculate_distance,
    find_nearby,
    start_location_tracking,
    record_location,
    stop_location_tracking,
    get_tracking_status
)

urlpatterns = [
    # Geocoding endpoints
    path('geocode/', geocode_address, name='geocode-address'),
    path('reverse/', reverse_geocode, name='reverse-geocode'),
    path('distance/', calculate_distance, name='calculate-distance'),
    path('nearby/', find_nearby, name='find-nearby'),
    
    # Location tracking endpoints
    path('tracking/start/', start_location_tracking, name='start-tracking'),
    path('tracking/record/', record_location, name='record-location'),
    path('tracking/stop/', stop_location_tracking, name='stop-tracking'),
    path('tracking/status/<int:inspection_id>/', get_tracking_status, name='tracking-status'),
]
