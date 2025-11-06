"""
Observer Pattern Implementation
Provides Observer interface and Subject base class for implementing the Observer design pattern.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
import logging


class Observer(ABC):
    """
    Observer Interface
    Classes that want to be notified of changes should implement this interface.
    """
    
    @abstractmethod
    def update(self, subject: 'Subject', data: Dict[str, Any]) -> None:
        """
        Called when the observed subject changes.
        
        Args:
            subject: The subject that changed
            data: Dictionary containing information about what changed
                  - 'event_type': Type of change (e.g., 'containers_updated', 'network_changed')
                  - 'data': The actual data payload
                  - Additional context-specific keys
        """
        pass


class Subject:
    """
    Subject Base Class
    Maintains a list of observers and notifies them of changes.
    """
    
    def __init__(self):
        """Initialize the subject with an empty observer list."""
        self._observers: List[Observer] = []
        self._lock = __import__('threading').Lock()
    
    def attach(self, observer: Observer) -> None:
        """
        Attach an observer to this subject.
        
        Args:
            observer: Observer instance to attach
        """
        with self._lock:
            if observer not in self._observers:
                self._observers.append(observer)
                logging.debug(f"Observer {observer.__class__.__name__} attached to {self.__class__.__name__}")
    
    def detach(self, observer: Observer) -> None:
        """
        Detach an observer from this subject.
        
        Args:
            observer: Observer instance to detach
        """
        with self._lock:
            if observer in self._observers:
                self._observers.remove(observer)
                logging.debug(f"Observer {observer.__class__.__name__} detached from {self.__class__.__name__}")
    
    def notifyObservers(self, event_type: str, data: Any = None, **kwargs) -> None:
        """
        Notify all attached observers about a change.
        
        Args:
            event_type: Type of event (e.g., 'containers_updated', 'network_changed')
            data: The data payload associated with this change
            **kwargs: Additional context-specific information
        """
        with self._lock:
            observers = self._observers.copy()
        
        notification_data = {
            'event_type': event_type,
            'data': data,
            **kwargs
        }
        
        logging.debug(f"{self.__class__.__name__} notifying {len(observers)} observers of '{event_type}'")
        
        # Use list comprehension with error handling - faster than explicit loop
        def notify_observer(observer):
            try:
                observer.update(self, notification_data)
                return None  # Success
            except Exception as e:
                logging.error(f"Error notifying observer {observer.__class__.__name__}: {e}", exc_info=True)
                return observer  # Failed
        
        # Notify all observers and collect failures in one pass
        failed_observers = [obs for obs in (notify_observer(o) for o in observers) if obs is not None]
        
        # Remove failed observers using set difference - faster than nested loop
        if failed_observers:
            with self._lock:
                failed_set = set(failed_observers)
                self._observers = [o for o in self._observers if o not in failed_set]
                if failed_set:
                    for observer in failed_set:
                        logging.warning(f"Removed failing observer {observer.__class__.__name__} after update error")
    
    def get_observer_count(self) -> int:
        """
        Get the number of attached observers.
        
        Returns:
            Number of observers
        """
        with self._lock:
            return len(self._observers)
