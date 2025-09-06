"""
Offline synchronization URLs for SmartLeakPro application.
"""
from django.urls import path
from apps.core.views.offline_sync import (
    prepare_offline_data,
    store_offline_data,
    get_offline_data,
    queue_sync_action,
    get_sync_queue,
    process_sync_queue,
    get_sync_conflicts,
    resolve_sync_conflict,
    check_online_status,
    bulk_sync_data
)

urlpatterns = [
    # Offline data management
    path('prepare/', prepare_offline_data, name='prepare-offline-data'),
    path('store/', store_offline_data, name='store-offline-data'),
    path('data/', get_offline_data, name='get-offline-data'),
    
    # Sync queue management
    path('queue/', get_sync_queue, name='get-sync-queue'),
    path('queue/', queue_sync_action, name='queue-sync-action'),
    path('sync/', process_sync_queue, name='process-sync-queue'),
    path('bulk-sync/', bulk_sync_data, name='bulk-sync-data'),
    
    # Conflict resolution
    path('conflicts/', get_sync_conflicts, name='get-sync-conflicts'),
    path('conflicts/resolve/', resolve_sync_conflict, name='resolve-sync-conflict'),
    
    # Status
    path('status/', check_online_status, name='check-online-status'),
]
