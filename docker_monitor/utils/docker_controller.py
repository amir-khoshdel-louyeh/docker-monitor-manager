"""
Docker Data Controller
Central controller that manages Docker data and notifies observers of changes.
Implements the Observer pattern Subject role.
"""

import logging
import threading
from typing import List, Dict, Any, Optional
from docker_monitor.utils.observer import Subject


class DockerDataController(Subject):
    """
    Central controller for Docker data management.
    
    This controller acts as a single source of truth for Docker data and notifies
    all registered observers when data changes. This improves UI responsiveness by
    decoupling data fetching from UI updates.
    
    Event Types:
        - 'containers_updated': Container list or stats changed
        - 'networks_updated': Network list changed
        - 'images_updated': Image list changed
        - 'volumes_updated': Volume list changed
        - 'docker_event': Real-time Docker event occurred
        - 'container_action': Container action completed (start, stop, etc.)
        - 'network_action': Network action completed
        - 'image_action': Image action completed
        - 'volume_action': Volume action completed
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern to ensure only one controller instance exists."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the controller."""
        # Only initialize once (singleton)
        if not hasattr(self, '_initialized'):
            super().__init__()
            self._initialized = True
            
            # Cache for Docker data
            self._containers_cache: List[Dict[str, Any]] = []
            self._networks_cache: List[Dict[str, Any]] = []
            self._images_cache: List[Dict[str, Any]] = []
            self._volumes_cache: List[Dict[str, Any]] = []
            
            # Thread-safe locks for cache access
            self._containers_lock = threading.Lock()
            self._networks_lock = threading.Lock()
            self._images_lock = threading.Lock()
            self._volumes_lock = threading.Lock()
            
            logging.info("DockerDataController initialized")
    
    # === Container Methods ===
    
    def update_containers(self, containers_data: List[Dict[str, Any]]) -> None:
        """
        Update container data and notify observers.
        
        Args:
            containers_data: List of container stats dictionaries
        """
        if containers_data is None:
            logging.warning("update_containers called with None")
            return
        
        if not isinstance(containers_data, list):
            logging.error(f"update_containers expected list, got {type(containers_data)}")
            return
        
        with self._containers_lock:
            self._containers_cache = containers_data
        
        self.notifyObservers('containers_updated', data=containers_data)
        logging.debug(f"Container data updated: {len(containers_data)} containers")
    
    def get_containers(self) -> List[Dict[str, Any]]:
        """
        Get cached container data.
        
        Returns:
            List of container stats dictionaries
        """
        with self._containers_lock:
            return self._containers_cache.copy()
    
    def notify_container_action(self, action: str, container_name: str, 
                                success: bool = True, error: Optional[str] = None) -> None:
        """
        Notify observers of a container action.
        
        Args:
            action: Action performed (start, stop, remove, etc.)
            container_name: Name of the container
            success: Whether the action succeeded
            error: Error message if action failed
        """
        self.notifyObservers(
            'container_action',
            data={
                'action': action,
                'container_name': container_name,
                'success': success,
                'error': error
            }
        )
    
    # === Network Methods ===
    
    def update_networks(self, networks_data: List[Dict[str, Any]]) -> None:
        """
        Update network data and notify observers.
        
        Args:
            networks_data: List of network dictionaries
        """
        if networks_data is None:
            logging.warning("update_networks called with None")
            return
        
        if not isinstance(networks_data, list):
            logging.error(f"update_networks expected list, got {type(networks_data)}")
            return
        
        with self._networks_lock:
            self._networks_cache = networks_data
        
        self.notifyObservers('networks_updated', data=networks_data)
        logging.debug(f"Network data updated: {len(networks_data)} networks")
    
    def get_networks(self) -> List[Dict[str, Any]]:
        """
        Get cached network data.
        
        Returns:
            List of network dictionaries
        """
        with self._networks_lock:
            return self._networks_cache.copy()
    
    def notify_network_action(self, action: str, network_name: str,
                             success: bool = True, error: Optional[str] = None) -> None:
        """
        Notify observers of a network action.
        
        Args:
            action: Action performed (create, remove, etc.)
            network_name: Name of the network
            success: Whether the action succeeded
            error: Error message if action failed
        """
        self.notifyObservers(
            'network_action',
            data={
                'action': action,
                'network_name': network_name,
                'success': success,
                'error': error
            }
        )
    
    # === Image Methods ===
    
    def update_images(self, images_data: List[Dict[str, Any]]) -> None:
        """
        Update image data and notify observers.
        
        Args:
            images_data: List of image dictionaries
        """
        if images_data is None:
            logging.warning("update_images called with None")
            return
        
        if not isinstance(images_data, list):
            logging.error(f"update_images expected list, got {type(images_data)}")
            return
        
        with self._images_lock:
            self._images_cache = images_data
        
        self.notifyObservers('images_updated', data=images_data)
        logging.debug(f"Image data updated: {len(images_data)} images")
    
    def get_images(self) -> List[Dict[str, Any]]:
        """
        Get cached image data.
        
        Returns:
            List of image dictionaries
        """
        with self._images_lock:
            return self._images_cache.copy()
    
    def notify_image_action(self, action: str, image_id: str,
                           success: bool = True, error: Optional[str] = None) -> None:
        """
        Notify observers of an image action.
        
        Args:
            action: Action performed (pull, remove, etc.)
            image_id: ID of the image
            success: Whether the action succeeded
            error: Error message if action failed
        """
        self.notifyObservers(
            'image_action',
            data={
                'action': action,
                'image_id': image_id,
                'success': success,
                'error': error
            }
        )
    
    # === Volume Methods ===
    
    def update_volumes(self, volumes_data: List[Dict[str, Any]]) -> None:
        """
        Update volume data and notify observers.
        
        Args:
            volumes_data: List of volume dictionaries
        """
        if volumes_data is None:
            logging.warning("update_volumes called with None")
            return
        
        if not isinstance(volumes_data, list):
            logging.error(f"update_volumes expected list, got {type(volumes_data)}")
            return
        
        with self._volumes_lock:
            self._volumes_cache = volumes_data
        
        self.notifyObservers('volumes_updated', data=volumes_data)
        logging.debug(f"Volume data updated: {len(volumes_data)} volumes")
    
    def get_volumes(self) -> List[Dict[str, Any]]:
        """
        Get cached volume data.
        
        Returns:
            List of volume dictionaries
        """
        with self._volumes_lock:
            return self._volumes_cache.copy()
    
    def notify_volume_action(self, action: str, volume_name: str,
                            success: bool = True, error: Optional[str] = None) -> None:
        """
        Notify observers of a volume action.
        
        Args:
            action: Action performed (create, remove, etc.)
            volume_name: Name of the volume
            success: Whether the action succeeded
            error: Error message if action failed
        """
        self.notifyObservers(
            'volume_action',
            data={
                'action': action,
                'volume_name': volume_name,
                'success': success,
                'error': error
            }
        )
    
    # === Docker Event Methods ===
    
    def notify_docker_event(self, event: Dict[str, Any]) -> None:
        """
        Notify observers of a real-time Docker event.
        
        Args:
            event: Docker event dictionary
        """
        self.notifyObservers('docker_event', data=event)
        logging.debug(f"Docker event: {event.get('Action')} on {event.get('Type')}")
    
    # === Utility Methods ===
    
    def clear_all_caches(self) -> None:
        """Clear all cached data."""
        with self._containers_lock:
            self._containers_cache = []
        with self._networks_lock:
            self._networks_cache = []
        with self._images_lock:
            self._images_cache = []
        with self._volumes_lock:
            self._volumes_cache = []
        
        logging.info("All Docker data caches cleared")
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics about cached data.
        
        Returns:
            Dictionary with counts of each data type and observer count
        """
        return {
            'containers': len(self._containers_cache),
            'networks': len(self._networks_cache),
            'images': len(self._images_cache),
            'volumes': len(self._volumes_cache),
            'observers': self.get_observer_count()
        }
    
    # === Optimized Batch Methods (No Loops) ===
    
    def update_all_resources(self, containers: Optional[List[Dict]] = None,
                            networks: Optional[List[Dict]] = None,
                            images: Optional[List[Dict]] = None,
                            volumes: Optional[List[Dict]] = None) -> None:
        """
        Batch update multiple resource types at once with a single notification.
        
        This is faster than calling individual update methods because:
        - Single lock acquisition per resource
        - Single notification to observers
        - Reduces context switching
        
        Args:
            containers: Container data (None = no update)
            networks: Network data (None = no update)
            images: Image data (None = no update)
            volumes: Volume data (None = no update)
        """
        updated_types = []
        
        if containers is not None:
            with self._containers_lock:
                self._containers_cache = containers
            updated_types.append(f"{len(containers)} containers")
        
        if networks is not None:
            with self._networks_lock:
                self._networks_cache = networks
            updated_types.append(f"{len(networks)} networks")
        
        if images is not None:
            with self._images_lock:
                self._images_cache = images
            updated_types.append(f"{len(images)} images")
        
        if volumes is not None:
            with self._volumes_lock:
                self._volumes_cache = volumes
            updated_types.append(f"{len(volumes)} volumes")
        
        if updated_types:
            # Single notification for all updates
            self.notifyObservers(
                'batch_updated',
                data={
                    'containers': containers,
                    'networks': networks,
                    'images': images,
                    'volumes': volumes
                }
            )
            logging.debug(f"Batch update: {', '.join(updated_types)}")
    
    def find_container_by_id(self, container_id: str) -> Optional[Dict[str, Any]]:
        """
        Fast container lookup using built-in next() with generator expression.
        O(n) but more efficient than explicit loop due to early termination.
        
        Args:
            container_id: Container ID (full or short)
            
        Returns:
            Container dict or None
        """
        with self._containers_lock:
            return next(
                (c for c in self._containers_cache 
                 if c.get('id', '').startswith(container_id) or c.get('name') == container_id),
                None
            )
    
    def find_containers_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Filter containers by status using list comprehension (faster than loop).
        
        Args:
            status: Container status (running, stopped, paused, etc.)
            
        Returns:
            List of matching containers
        """
        with self._containers_lock:
            return [c for c in self._containers_cache if c.get('status') == status]
    
    def find_network_by_name(self, network_name: str) -> Optional[Dict[str, Any]]:
        """
        Fast network lookup using generator expression.
        
        Args:
            network_name: Network name
            
        Returns:
            Network dict or None
        """
        with self._networks_lock:
            return next(
                (n for n in self._networks_cache if n.get('name') == network_name),
                None
            )
    
    def find_image_by_tag(self, tag: str) -> Optional[Dict[str, Any]]:
        """
        Fast image lookup by tag using generator expression.
        
        Args:
            tag: Image tag (e.g., 'nginx:latest')
            
        Returns:
            Image dict or None
        """
        with self._images_lock:
            return next(
                (img for img in self._images_cache 
                 if tag in img.get('repo_tags', [])),
                None
            )
    
    def find_volume_by_name(self, volume_name: str) -> Optional[Dict[str, Any]]:
        """
        Fast volume lookup using generator expression.
        
        Args:
            volume_name: Volume name
            
        Returns:
            Volume dict or None
        """
        with self._volumes_lock:
            return next(
                (v for v in self._volumes_cache if v.get('Name') == volume_name),
                None
            )
    
    def get_resource_counts(self) -> Dict[str, int]:
        """
        Fast count of resources using len() (O(1) operation).
        Faster than iterating through collections.
        
        Returns:
            Dictionary with resource counts
        """
        # Using len() is O(1) - no iteration needed
        return {
            'total_containers': len(self._containers_cache),
            'running_containers': sum(1 for c in self._containers_cache if c.get('status') == 'running'),
            'stopped_containers': sum(1 for c in self._containers_cache if c.get('status') in ('exited', 'stopped')),
            'total_networks': len(self._networks_cache),
            'total_images': len(self._images_cache),
            'total_volumes': len(self._volumes_cache),
            'total_observers': self.get_observer_count()
        }
    
    def filter_containers_by_criteria(self, **criteria) -> List[Dict[str, Any]]:
        """
        Filter containers using multiple criteria with efficient all() function.
        Uses generator expression and all() to short-circuit on first False.
        
        Example:
            filter_containers_by_criteria(status='running', cpu=lambda x: float(x) > 50)
        
        Args:
            **criteria: Key-value pairs where value can be:
                       - Exact match value
                       - Callable for custom comparison
        
        Returns:
            Filtered container list
        """
        with self._containers_lock:
            def matches_criteria(container: Dict[str, Any]) -> bool:
                return all(
                    (callable(value) and value(container.get(key))) or 
                    container.get(key) == value
                    for key, value in criteria.items()
                )
            
            return [c for c in self._containers_cache if matches_criteria(c)]
    
    def bulk_notify_actions(self, actions: List[Dict[str, Any]]) -> None:
        """
        Notify observers of multiple actions at once.
        More efficient than individual notifications.
        
        Args:
            actions: List of action dicts with keys:
                    - type: 'container', 'network', 'image', 'volume'
                    - action: action name
                    - target: target name/id
                    - success: bool
                    - error: optional error message
        """
        self.notifyObservers(
            'bulk_actions',
            data={'actions': actions, 'count': len(actions)}
        )
        logging.debug(f"Bulk notification: {len(actions)} actions")
    
    def get_all_resources_snapshot(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get a complete snapshot of all resources in a single operation.
        More efficient than calling individual getters.
        Uses dict comprehension for fast dictionary creation.
        
        Returns:
            Dictionary containing all cached data
        """
        # Single lock acquisition per resource type
        containers = self.get_containers()
        networks = self.get_networks()
        images = self.get_images()
        volumes = self.get_volumes()
        
        # Fast dict creation using dict literal
        return {
            'containers': containers,
            'networks': networks,
            'images': images,
            'volumes': volumes,
            'timestamp': __import__('time').time(),
            'stats': self.get_stats()
        }
    
    def search_resources(self, query: str, 
                        search_types: Optional[List[str]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fast search across all resource types using case-insensitive matching.
        Uses list comprehensions and any() for efficient searching.
        
        Args:
            query: Search string (case-insensitive)
            search_types: Resource types to search ['containers', 'networks', 'images', 'volumes']
                         None = search all
        
        Returns:
            Dictionary with search results per type
        """
        query_lower = query.lower()
        search_types = search_types or ['containers', 'networks', 'images', 'volumes']
        results = {}
        
        if 'containers' in search_types:
            with self._containers_lock:
                results['containers'] = [
                    c for c in self._containers_cache
                    if any(query_lower in str(v).lower() for v in c.values())
                ]
        
        if 'networks' in search_types:
            with self._networks_lock:
                results['networks'] = [
                    n for n in self._networks_cache
                    if any(query_lower in str(v).lower() for v in n.values())
                ]
        
        if 'images' in search_types:
            with self._images_lock:
                results['images'] = [
                    img for img in self._images_cache
                    if any(query_lower in str(v).lower() for v in img.values())
                ]
        
        if 'volumes' in search_types:
            with self._volumes_lock:
                results['volumes'] = [
                    v for v in self._volumes_cache
                    if any(query_lower in str(val).lower() for val in v.values())
                ]
        
        return results
    
    def compute_resource_metrics(self) -> Dict[str, Any]:
        """
        Compute metrics using efficient built-in functions and list comprehensions.
        Uses map(), filter(), and sum() for optimal performance.
        
        Returns:
            Dictionary with computed metrics
        """
        with self._containers_lock:
            containers = self._containers_cache.copy()
        
        if not containers:
            return {
                'avg_cpu': 0.0,
                'avg_ram': 0.0,
                'max_cpu': 0.0,
                'max_ram': 0.0,
                'total_containers': 0,
                'running_containers': 0
            }
        
        # Use list comprehension with filter for running containers
        running_containers = [c for c in containers if c.get('status') == 'running']
        
        # Use generator expressions with sum() for efficiency
        cpu_values = [float(c.get('cpu', 0)) for c in running_containers]
        ram_values = [float(c.get('ram', 0)) for c in running_containers]
        
        return {
            'avg_cpu': sum(cpu_values) / len(cpu_values) if cpu_values else 0.0,
            'avg_ram': sum(ram_values) / len(ram_values) if ram_values else 0.0,
            'max_cpu': max(cpu_values) if cpu_values else 0.0,
            'max_ram': max(ram_values) if ram_values else 0.0,
            'total_containers': len(containers),
            'running_containers': len(running_containers)
        }


# Global singleton instance
_controller = None


def get_docker_controller() -> DockerDataController:
    """
    Get the global Docker data controller instance.
    
    Returns:
        DockerDataController singleton instance
    """
    global _controller
    if _controller is None:
        _controller = DockerDataController()
    return _controller
