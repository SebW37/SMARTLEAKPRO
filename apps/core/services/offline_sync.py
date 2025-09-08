"""
Offline synchronization services for SmartLeakPro application.
"""
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from django.core.cache import cache
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
# # from django.contrib.gis.geos import Point

logger = logging.getLogger(__name__)


class OfflineSyncService:
    """Service for handling offline data synchronization."""
    
    def __init__(self):
        self.offline_key_prefix = "offline_data"
        self.sync_queue_prefix = "sync_queue"
        self.conflict_prefix = "sync_conflicts"
    
    def store_offline_data(self, user_id: int, data_type: str, 
                          object_id: str, data: Dict[str, Any]) -> bool:
        """
        Store data for offline use.
        
        Args:
            user_id (int): User ID
            data_type (str): Type of data (e.g., 'inspection', 'client', 'intervention')
            object_id (str): Unique identifier for the object
            data (dict): Data to store
            
        Returns:
            bool: True if data stored successfully
        """
        try:
            cache_key = f"{self.offline_key_prefix}:{user_id}:{data_type}:{object_id}"
            offline_data = {
                'data': data,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'last_modified': datetime.now(timezone.utc).isoformat(),
                'user_id': user_id,
                'data_type': data_type,
                'object_id': object_id,
                'sync_status': 'offline'
            }
            
            # Store for 7 days
            cache.set(cache_key, offline_data, 604800)
            return True
            
        except Exception as e:
            logger.error(f"Failed to store offline data: {str(e)}")
            return False
    
    def get_offline_data(self, user_id: int, data_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve offline data for a user.
        
        Args:
            user_id (int): User ID
            data_type (str, optional): Filter by data type
            
        Returns:
            list: List of offline data objects
        """
        try:
            pattern = f"{self.offline_key_prefix}:{user_id}:*"
            if data_type:
                pattern = f"{self.offline_key_prefix}:{user_id}:{data_type}:*"
            
            # Note: This is a simplified version. In production, you'd want to use
            # a more efficient method to get keys by pattern
            offline_data = []
            
            # For demonstration, we'll use a simple approach
            # In production, consider using Redis SCAN or a database solution
            
            return offline_data
            
        except Exception as e:
            logger.error(f"Failed to get offline data: {str(e)}")
            return []
    
    def queue_for_sync(self, user_id: int, action: str, data_type: str, 
                      object_id: str, data: Dict[str, Any]) -> bool:
        """
        Queue an action for synchronization when online.
        
        Args:
            user_id (int): User ID
            action (str): Action to perform ('create', 'update', 'delete')
            data_type (str): Type of data
            object_id (str): Object identifier
            data (dict): Data to sync
            
        Returns:
            bool: True if queued successfully
        """
        try:
            queue_key = f"{self.sync_queue_prefix}:{user_id}"
            
            sync_item = {
                'id': f"{data_type}_{object_id}_{datetime.now(timezone.utc).timestamp()}",
                'action': action,
                'data_type': data_type,
                'object_id': object_id,
                'data': data,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'user_id': user_id,
                'status': 'pending'
            }
            
            # Get existing queue
            queue = cache.get(queue_key, [])
            queue.append(sync_item)
            
            # Store queue for 7 days
            cache.set(queue_key, queue, 604800)
            return True
            
        except Exception as e:
            logger.error(f"Failed to queue sync item: {str(e)}")
            return False
    
    def get_sync_queue(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get pending sync items for a user.
        
        Args:
            user_id (int): User ID
            
        Returns:
            list: List of pending sync items
        """
        try:
            queue_key = f"{self.sync_queue_prefix}:{user_id}"
            return cache.get(queue_key, [])
            
        except Exception as e:
            logger.error(f"Failed to get sync queue: {str(e)}")
            return []
    
    def process_sync_queue(self, user_id: int) -> Dict[str, Any]:
        """
        Process pending sync items for a user.
        
        Args:
            user_id (int): User ID
            
        Returns:
            dict: Sync results
        """
        results = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'conflicts': 0,
            'errors': []
        }
        
        try:
            queue = self.get_sync_queue(user_id)
            
            for item in queue:
                results['processed'] += 1
                
                try:
                    success = self._process_sync_item(item)
                    if success:
                        results['successful'] += 1
                    else:
                        results['failed'] += 1
                        
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(f"Item {item['id']}: {str(e)}")
            
            # Clear processed queue
            if results['processed'] > 0:
                self._clear_sync_queue(user_id)
            
        except Exception as e:
            logger.error(f"Failed to process sync queue: {str(e)}")
            results['errors'].append(str(e))
        
        return results
    
    def _process_sync_item(self, item: Dict[str, Any]) -> bool:
        """
        Process a single sync item.
        
        Args:
            item (dict): Sync item to process
            
        Returns:
            bool: True if processed successfully
        """
        try:
            action = item['action']
            data_type = item['data_type']
            object_id = item['object_id']
            data = item['data']
            
            # Get the appropriate model class
            model_class = self._get_model_class(data_type)
            if not model_class:
                return False
            
            with transaction.atomic():
                if action == 'create':
                    return self._create_object(model_class, data)
                elif action == 'update':
                    return self._update_object(model_class, object_id, data)
                elif action == 'delete':
                    return self._delete_object(model_class, object_id)
                    
        except Exception as e:
            logger.error(f"Failed to process sync item: {str(e)}")
            return False
        
        return False
    
    def _get_model_class(self, data_type: str):
        """Get Django model class for a data type."""
        model_mapping = {
            'client': 'apps.clients.models.Client',
            'client_site': 'apps.clients.models.ClientSite',
            'intervention': 'apps.interventions.models.Intervention',
            'inspection': 'apps.inspections.models.Inspection',
            'report': 'apps.reports.models.Report',
        }
        
        if data_type not in model_mapping:
            return None
        
        try:
            from django.apps import apps
            app_label, model_name = model_mapping[data_type].split('.')[-2:]
            return apps.get_model(app_label, model_name)
        except Exception:
            return None
    
    def _create_object(self, model_class, data: Dict[str, Any]) -> bool:
        """Create a new object."""
        try:
            # Process location data if present
            if 'location' in data and data['location']:
                lat = data['location'].get('latitude')
                lng = data['location'].get('longitude')
                if lat and lng:
                    data['location'] = # Point(lng, lat)
            
            obj = model_class.objects.create(**data)
            return True
        except Exception as e:
            logger.error(f"Failed to create object: {str(e)}")
            return False
    
    def _update_object(self, model_class, object_id: str, data: Dict[str, Any]) -> bool:
        """Update an existing object."""
        try:
            obj = model_class.objects.get(id=object_id)
            
            # Check for conflicts (simplified version)
            if hasattr(obj, 'updated_at') and 'last_modified' in data:
                obj_modified = obj.updated_at.isoformat()
                data_modified = data.get('last_modified')
                
                if obj_modified > data_modified:
                    # Conflict detected
                    self._handle_conflict(model_class, object_id, obj, data)
                    return False
            
            # Process location data if present
            if 'location' in data and data['location']:
                lat = data['location'].get('latitude')
                lng = data['location'].get('longitude')
                if lat and lng:
                    data['location'] = # Point(lng, lat)
            
            # Update object
            for field, value in data.items():
                if hasattr(obj, field):
                    setattr(obj, field, value)
            
            obj.save()
            return True
            
        except model_class.DoesNotExist:
            # Object doesn't exist, try to create it
            return self._create_object(model_class, data)
        except Exception as e:
            logger.error(f"Failed to update object: {str(e)}")
            return False
    
    def _delete_object(self, model_class, object_id: str) -> bool:
        """Delete an object."""
        try:
            obj = model_class.objects.get(id=object_id)
            obj.delete()
            return True
        except model_class.DoesNotExist:
            # Object already deleted
            return True
        except Exception as e:
            logger.error(f"Failed to delete object: {str(e)}")
            return False
    
    def _handle_conflict(self, model_class, object_id: str, 
                        server_obj, client_data: Dict[str, Any]):
        """Handle sync conflicts."""
        try:
            conflict_key = f"{self.conflict_prefix}:{object_id}"
            conflict_data = {
                'model': f"{model_class._meta.app_label}.{model_class._meta.model_name}",
                'object_id': object_id,
                'server_data': self._serialize_object(server_obj),
                'client_data': client_data,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Store conflict for 30 days
            cache.set(conflict_key, conflict_data, 2592000)
            
        except Exception as e:
            logger.error(f"Failed to handle conflict: {str(e)}")
    
    def _serialize_object(self, obj) -> Dict[str, Any]:
        """Serialize Django object to dictionary."""
        try:
            from django.core import serializers
            serialized = serializers.serialize('json', [obj])
            return json.loads(serialized)[0]['fields']
        except Exception:
            return {}
    
    def _clear_sync_queue(self, user_id: int):
        """Clear the sync queue for a user."""
        try:
            queue_key = f"{self.sync_queue_prefix}:{user_id}"
            cache.delete(queue_key)
        except Exception as e:
            logger.error(f"Failed to clear sync queue: {str(e)}")
    
    def get_conflicts(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get sync conflicts for a user.
        
        Args:
            user_id (int): User ID
            
        Returns:
            list: List of conflicts
        """
        # This is a simplified implementation
        # In production, you'd want to track conflicts per user
        return []
    
    def resolve_conflict(self, conflict_id: str, resolution: str, 
                        resolved_data: Dict[str, Any]) -> bool:
        """
        Resolve a sync conflict.
        
        Args:
            conflict_id (str): Conflict identifier
            resolution (str): Resolution type ('use_server', 'use_client', 'merge')
            resolved_data (dict): Resolved data if merging
            
        Returns:
            bool: True if conflict resolved successfully
        """
        try:
            conflict_key = f"{self.conflict_prefix}:{conflict_id}"
            conflict = cache.get(conflict_key)
            
            if not conflict:
                return False
            
            # Apply resolution logic here
            if resolution == 'use_server':
                # Keep server data, discard client changes
                pass
            elif resolution == 'use_client':
                # Apply client data
                pass
            elif resolution == 'merge':
                # Apply merged data
                pass
            
            # Remove conflict
            cache.delete(conflict_key)
            return True
            
        except Exception as e:
            logger.error(f"Failed to resolve conflict: {str(e)}")
            return False


class OfflineDataManager:
    """Manager for offline data operations."""
    
    def __init__(self):
        self.sync_service = OfflineSyncService()
    
    def prepare_offline_data(self, user_id: int, data_types: List[str]) -> Dict[str, Any]:
        """
        Prepare data for offline use.
        
        Args:
            user_id (int): User ID
            data_types (list): Types of data to prepare
            
        Returns:
            dict: Prepared offline data
        """
        offline_data = {}
        
        try:
            for data_type in data_types:
                offline_data[data_type] = self._get_user_data(user_id, data_type)
                
        except Exception as e:
            logger.error(f"Failed to prepare offline data: {str(e)}")
        
        return offline_data
    
    def _get_user_data(self, user_id: int, data_type: str) -> List[Dict[str, Any]]:
        """Get user-specific data for a data type."""
        from django.contrib.auth.models import User
        
        try:
            user = User.objects.get(id=user_id)
            
            if data_type == 'clients':
                from apps.clients.models import Client
                queryset = Client.objects.filter(created_by=user)
            elif data_type == 'interventions':
                from apps.interventions.models import Intervention
                queryset = Intervention.objects.filter(assigned_technician=user)
            elif data_type == 'inspections':
                from apps.inspections.models import Inspection
                queryset = Inspection.objects.filter(inspector=user)
            else:
                return []
            
            # Serialize data
            data = []
            for obj in queryset:
                serialized = self.sync_service._serialize_object(obj)
                serialized['id'] = obj.id
                
                # Handle location fields
                if hasattr(obj, 'location') and obj.location:
                    serialized['location'] = {
                        'latitude': obj.location.y,
                        'longitude': obj.location.x
                    }
                
                data.append(serialized)
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to get user data: {str(e)}")
            return []
    
    def sync_offline_changes(self, user_id: int) -> Dict[str, Any]:
        """
        Synchronize offline changes for a user.
        
        Args:
            user_id (int): User ID
            
        Returns:
            dict: Sync results
        """
        return self.sync_service.process_sync_queue(user_id)
    
    def is_online(self) -> bool:
        """
        Check if the system is online.
        
        Returns:
            bool: True if online
        """
        try:
            import requests
            response = requests.get('https://httpbin.org/status/200', timeout=5)
            return response.status_code == 200
        except:
            return False


# Service instances
offline_sync_service = OfflineSyncService()
offline_data_manager = OfflineDataManager()
