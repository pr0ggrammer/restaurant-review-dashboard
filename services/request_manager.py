"""
Concurrent Request Management Service

This module provides utilities for handling concurrent API requests,
connection pooling, and resource management for the dashboard application.
"""

import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Callable, Optional
from contextlib import contextmanager
import queue
from collections import defaultdict

# Configure logging
logger = logging.getLogger(__name__)

class RequestManager:
    """
    Manages concurrent requests with connection pooling and resource management.
    Ensures thread-safe operations and optimal resource utilization.
    """
    
    def __init__(self, max_workers: int = 10, max_queue_size: int = 100):
        """
        Initialize the request manager with configurable concurrency limits.
        
        Args:
            max_workers: Maximum number of concurrent worker threads
            max_queue_size: Maximum size of the request queue
        """
        self.max_workers = max_workers
        self.max_queue_size = max_queue_size
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.request_queue = queue.Queue(maxsize=max_queue_size)
        self.active_requests = defaultdict(int)
        self.request_lock = threading.RLock()
        self.stats = {
            'total_requests': 0,
            'completed_requests': 0,
            'failed_requests': 0,
            'active_requests': 0,
            'queue_size': 0
        }
        
    def submit_request(self, func: Callable, *args, **kwargs) -> Any:
        """
        Submit a request for concurrent execution with resource management.
        
        Args:
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Future object representing the pending result
            
        Raises:
            queue.Full: If the request queue is at capacity
        """
        with self.request_lock:
            if self.request_queue.qsize() >= self.max_queue_size:
                raise queue.Full("Request queue is at capacity")
            
            self.stats['total_requests'] += 1
            self.stats['active_requests'] += 1
            self.stats['queue_size'] = self.request_queue.qsize()
            
        future = self.executor.submit(self._execute_with_tracking, func, *args, **kwargs)
        return future
    
    def _execute_with_tracking(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function with request tracking and error handling.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Result of the function execution
        """
        start_time = time.time()
        thread_id = threading.get_ident()
        
        try:
            with self.request_lock:
                self.active_requests[thread_id] += 1
                
            logger.debug(f"Executing request on thread {thread_id}")
            result = func(*args, **kwargs)
            
            with self.request_lock:
                self.stats['completed_requests'] += 1
                
            duration = time.time() - start_time
            logger.debug(f"Request completed in {duration:.3f}s on thread {thread_id}")
            
            return result
            
        except Exception as e:
            with self.request_lock:
                self.stats['failed_requests'] += 1
                
            logger.error(f"Request failed on thread {thread_id}: {str(e)}")
            raise
            
        finally:
            with self.request_lock:
                self.active_requests[thread_id] -= 1
                if self.active_requests[thread_id] <= 0:
                    del self.active_requests[thread_id]
                self.stats['active_requests'] -= 1
    
    def execute_batch(self, requests: List[Dict[str, Any]], timeout: Optional[float] = None) -> List[Any]:
        """
        Execute multiple requests concurrently and return results.
        
        Args:
            requests: List of request dictionaries with 'func', 'args', 'kwargs'
            timeout: Maximum time to wait for all requests to complete
            
        Returns:
            List of results in the same order as input requests
        """
        futures = []
        results = [None] * len(requests)
        
        # Submit all requests
        for i, req in enumerate(requests):
            func = req['func']
            args = req.get('args', ())
            kwargs = req.get('kwargs', {})
            
            try:
                future = self.submit_request(func, *args, **kwargs)
                futures.append((i, future))
            except queue.Full:
                logger.warning(f"Request {i} dropped due to queue capacity")
                results[i] = {'error': 'Queue capacity exceeded'}
        
        # Collect results
        for i, future in futures:
            try:
                result = future.result(timeout=timeout)
                results[i] = result
            except Exception as e:
                logger.error(f"Batch request {i} failed: {str(e)}")
                results[i] = {'error': str(e)}
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get current statistics about request processing.
        
        Returns:
            Dictionary containing request statistics
        """
        with self.request_lock:
            stats_copy = self.stats.copy()
            stats_copy['queue_size'] = self.request_queue.qsize()
            stats_copy['active_threads'] = len(self.active_requests)
            
        return stats_copy
    
    def shutdown(self, wait: bool = True):
        """
        Shutdown the request manager and cleanup resources.
        
        Args:
            wait: Whether to wait for pending requests to complete
        """
        logger.info("Shutting down request manager")
        self.executor.shutdown(wait=wait)
        
        with self.request_lock:
            self.stats['active_requests'] = 0
            self.active_requests.clear()

# Global request manager instance
_request_manager = None
_manager_lock = threading.Lock()

def get_request_manager() -> RequestManager:
    """
    Get the global request manager instance (singleton pattern).
    
    Returns:
        RequestManager instance
    """
    global _request_manager
    
    if _request_manager is None:
        with _manager_lock:
            if _request_manager is None:
                _request_manager = RequestManager()
                
    return _request_manager

@contextmanager
def managed_request():
    """
    Context manager for handling requests with automatic resource cleanup.
    
    Usage:
        with managed_request() as manager:
            result = manager.submit_request(some_function, arg1, arg2)
    """
    manager = get_request_manager()
    try:
        yield manager
    except Exception as e:
        logger.error(f"Error in managed request: {str(e)}")
        raise
    finally:
        # Cleanup is handled automatically by the manager
        pass

class ConnectionPool:
    """
    Simple connection pool for managing API connections.
    """
    
    def __init__(self, max_connections: int = 20):
        """
        Initialize connection pool.
        
        Args:
            max_connections: Maximum number of concurrent connections
        """
        self.max_connections = max_connections
        self.semaphore = threading.Semaphore(max_connections)
        self.active_connections = 0
        self.connection_lock = threading.Lock()
    
    @contextmanager
    def get_connection(self):
        """
        Get a connection from the pool.
        
        Yields:
            Connection context (placeholder for actual connection)
        """
        acquired = self.semaphore.acquire(blocking=True, timeout=30)
        if not acquired:
            raise TimeoutError("Could not acquire connection within timeout")
        
        try:
            with self.connection_lock:
                self.active_connections += 1
                
            logger.debug(f"Acquired connection, active: {self.active_connections}")
            yield self  # In a real implementation, this would be an actual connection
            
        finally:
            with self.connection_lock:
                self.active_connections -= 1
                
            self.semaphore.release()
            logger.debug(f"Released connection, active: {self.active_connections}")
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get connection pool statistics.
        
        Returns:
            Dictionary with connection statistics
        """
        with self.connection_lock:
            return {
                'max_connections': self.max_connections,
                'active_connections': self.active_connections,
                'available_connections': self.max_connections - self.active_connections
            }

# Global connection pool instance
_connection_pool = None
_pool_lock = threading.Lock()

def get_connection_pool() -> ConnectionPool:
    """
    Get the global connection pool instance (singleton pattern).
    
    Returns:
        ConnectionPool instance
    """
    global _connection_pool
    
    if _connection_pool is None:
        with _pool_lock:
            if _connection_pool is None:
                _connection_pool = ConnectionPool()
                
    return _connection_pool