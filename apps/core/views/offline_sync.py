"""
Offline synchronization views for SmartLeakPro application.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from apps.core.services.offline_sync import offline_sync_service, offline_data_manager
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def prepare_offline_data(request):
    """
    Prepare data for offline use.
    
    POST /api/offline/prepare/
    {
        "data_types": ["clients", "interventions", "inspections"]
    }
    """
    try:
        data_types = request.data.get('data_types', [])
        if not data_types:
            data_types = ['clients', 'interventions', 'inspections']
        
        offline_data = offline_data_manager.prepare_offline_data(request.user.id, data_types)
        
        return Response({
            'success': True,
            'data': offline_data,
            'user_id': request.user.id,
            'prepared_types': data_types
        })
        
    except Exception as e:
        logger.error(f"Prepare offline data error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def store_offline_data(request):
    """
    Store data for offline use.
    
    POST /api/offline/store/
    {
        "data_type": "inspection",
        "object_id": "123",
        "data": {...}
    }
    """
    try:
        data_type = request.data.get('data_type')
        object_id = request.data.get('object_id')
        data = request.data.get('data')
        
        if not all([data_type, object_id, data]):
            return Response(
                {'error': 'data_type, object_id, and data are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success = offline_sync_service.store_offline_data(
            request.user.id, data_type, object_id, data
        )
        
        if success:
            return Response({
                'success': True,
                'message': 'Data stored for offline use'
            })
        else:
            return Response(
                {'error': 'Failed to store offline data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"Store offline data error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_offline_data(request):
    """
    Get offline data for the user.
    
    GET /api/offline/data/?data_type=inspections
    """
    try:
        data_type = request.query_params.get('data_type')
        
        offline_data = offline_sync_service.get_offline_data(request.user.id, data_type)
        
        return Response({
            'success': True,
            'data': offline_data,
            'data_type': data_type,
            'count': len(offline_data)
        })
        
    except Exception as e:
        logger.error(f"Get offline data error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def queue_sync_action(request):
    """
    Queue an action for synchronization.
    
    POST /api/offline/queue/
    {
        "action": "create",
        "data_type": "inspection",
        "object_id": "temp_123",
        "data": {...}
    }
    """
    try:
        action = request.data.get('action')
        data_type = request.data.get('data_type')
        object_id = request.data.get('object_id')
        data = request.data.get('data')
        
        if not all([action, data_type, object_id]):
            return Response(
                {'error': 'action, data_type, and object_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        valid_actions = ['create', 'update', 'delete']
        if action not in valid_actions:
            return Response(
                {'error': f'Invalid action. Must be one of: {valid_actions}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success = offline_sync_service.queue_for_sync(
            request.user.id, action, data_type, object_id, data or {}
        )
        
        if success:
            return Response({
                'success': True,
                'message': 'Action queued for synchronization'
            })
        else:
            return Response(
                {'error': 'Failed to queue sync action'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"Queue sync action error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sync_queue(request):
    """
    Get pending sync items for the user.
    
    GET /api/offline/queue/
    """
    try:
        sync_queue = offline_sync_service.get_sync_queue(request.user.id)
        
        return Response({
            'success': True,
            'queue': sync_queue,
            'count': len(sync_queue)
        })
        
    except Exception as e:
        logger.error(f"Get sync queue error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_sync_queue(request):
    """
    Process pending sync items.
    
    POST /api/offline/sync/
    """
    try:
        results = offline_sync_service.process_sync_queue(request.user.id)
        
        return Response({
            'success': True,
            'sync_results': results
        })
        
    except Exception as e:
        logger.error(f"Process sync queue error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sync_conflicts(request):
    """
    Get sync conflicts for the user.
    
    GET /api/offline/conflicts/
    """
    try:
        conflicts = offline_sync_service.get_conflicts(request.user.id)
        
        return Response({
            'success': True,
            'conflicts': conflicts,
            'count': len(conflicts)
        })
        
    except Exception as e:
        logger.error(f"Get sync conflicts error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resolve_sync_conflict(request):
    """
    Resolve a sync conflict.
    
    POST /api/offline/conflicts/resolve/
    {
        "conflict_id": "123",
        "resolution": "use_client",
        "resolved_data": {...}
    }
    """
    try:
        conflict_id = request.data.get('conflict_id')
        resolution = request.data.get('resolution')
        resolved_data = request.data.get('resolved_data', {})
        
        if not conflict_id or not resolution:
            return Response(
                {'error': 'conflict_id and resolution are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        valid_resolutions = ['use_server', 'use_client', 'merge']
        if resolution not in valid_resolutions:
            return Response(
                {'error': f'Invalid resolution. Must be one of: {valid_resolutions}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success = offline_sync_service.resolve_conflict(
            conflict_id, resolution, resolved_data
        )
        
        if success:
            return Response({
                'success': True,
                'message': 'Conflict resolved successfully'
            })
        else:
            return Response(
                {'error': 'Failed to resolve conflict'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"Resolve sync conflict error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_online_status(request):
    """
    Check if the system is online.
    
    GET /api/offline/status/
    """
    try:
        is_online = offline_data_manager.is_online()
        
        return Response({
            'success': True,
            'online': is_online,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Check online status error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_sync_data(request):
    """
    Bulk synchronization of offline data.
    
    POST /api/offline/bulk-sync/
    {
        "sync_items": [
            {
                "action": "create",
                "data_type": "inspection",
                "object_id": "temp_123",
                "data": {...}
            },
            ...
        ]
    }
    """
    try:
        sync_items = request.data.get('sync_items', [])
        
        if not sync_items:
            return Response(
                {'error': 'sync_items are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = {
            'total': len(sync_items),
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        for item in sync_items:
            try:
                action = item.get('action')
                data_type = item.get('data_type')
                object_id = item.get('object_id')
                data = item.get('data', {})
                
                if not all([action, data_type, object_id]):
                    results['failed'] += 1
                    results['errors'].append(f"Invalid item: missing required fields")
                    continue
                
                success = offline_sync_service.queue_for_sync(
                    request.user.id, action, data_type, object_id, data
                )
                
                if success:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Failed to queue item {object_id}")
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Error processing item: {str(e)}")
        
        # Process the queued items
        if results['successful'] > 0:
            sync_results = offline_sync_service.process_sync_queue(request.user.id)
            results['sync_results'] = sync_results
        
        return Response({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Bulk sync data error: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
