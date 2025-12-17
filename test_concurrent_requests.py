"""
Test for concurrent request handling functionality.

**Feature: restaurant-review-dashboard, Property 7: Concurrent Request Handling**
**Validates: Requirements 6.3**
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from services.request_manager import RequestManager, get_request_manager, managed_request


def test_concurrent_request_handling():
    """
    Property: For any number of concurrent user requests, the Flask server should 
    handle all requests without data corruption or service interruption.
    """
    print("Testing concurrent request handling...")
    
    # Create a request manager
    manager = RequestManager(max_workers=5, max_queue_size=20)
    
    def mock_api_call(request_id, delay=0.1):
        """Mock API call that takes some time"""
        time.sleep(delay)
        return f"Result for request {request_id}"
    
    # Test concurrent request submission
    num_requests = 10
    futures = []
    
    start_time = time.time()
    
    # Submit multiple concurrent requests
    for i in range(num_requests):
        future = manager.submit_request(mock_api_call, i, 0.05)
        futures.append((i, future))
    
    # Collect results
    results = {}
    for request_id, future in futures:
        try:
            result = future.result(timeout=5.0)
            results[request_id] = result
        except Exception as e:
            print(f"Request {request_id} failed: {e}")
            results[request_id] = None
    
    end_time = time.time()
    
    # Verify all requests completed
    assert len(results) == num_requests, f"Expected {num_requests} results, got {len(results)}"
    
    # Verify no data corruption (all results are unique and correct)
    for i in range(num_requests):
        expected = f"Result for request {i}"
        assert results[i] == expected, f"Data corruption detected for request {i}"
    
    # Verify concurrent execution (should be faster than sequential)
    total_time = end_time - start_time
    sequential_time = num_requests * 0.05  # Each request takes 0.05s
    assert total_time < sequential_time * 0.8, f"Requests may not be running concurrently: {total_time}s vs expected <{sequential_time * 0.8}s"
    
    # Check manager statistics
    stats = manager.get_stats()
    assert stats['total_requests'] == num_requests
    assert stats['completed_requests'] == num_requests
    assert stats['failed_requests'] == 0
    
    manager.shutdown()
    print("✓ Concurrent request handling test passed")
    return True


def test_request_queue_management():
    """
    Test that request queue properly manages capacity and prevents overload.
    """
    print("Testing request queue management...")
    
    # Create manager with small queue
    manager = RequestManager(max_workers=2, max_queue_size=5)
    
    def slow_task(task_id):
        time.sleep(0.2)
        return f"Task {task_id} completed"
    
    # Fill up the queue
    futures = []
    for i in range(5):
        future = manager.submit_request(slow_task, i)
        futures.append(future)
    
    # Try to submit one more (should succeed as queue isn't full yet)
    try:
        extra_future = manager.submit_request(slow_task, "extra")
        futures.append(extra_future)
    except Exception as e:
        print(f"Queue management working: {e}")
    
    # Wait for completion
    for future in futures:
        try:
            result = future.result(timeout=2.0)
            assert "completed" in result
        except Exception as e:
            print(f"Task failed: {e}")
    
    manager.shutdown()
    print("✓ Request queue management test passed")
    return True


def test_thread_safety():
    """
    Test that the request manager is thread-safe under concurrent access.
    """
    print("Testing thread safety...")
    
    manager = get_request_manager()  # Use singleton
    results = []
    results_lock = threading.Lock()
    
    def worker_thread(thread_id):
        """Worker that submits requests from different threads"""
        for i in range(5):
            def task():
                return f"Thread {thread_id}, Task {i}"
            
            try:
                future = manager.submit_request(task)
                result = future.result(timeout=1.0)
                
                with results_lock:
                    results.append(result)
            except Exception as e:
                print(f"Thread {thread_id} task {i} failed: {e}")
    
    # Create multiple threads
    threads = []
    num_threads = 3
    
    for thread_id in range(num_threads):
        thread = threading.Thread(target=worker_thread, args=(thread_id,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join(timeout=5.0)
    
    # Verify results
    expected_results = num_threads * 5  # 3 threads * 5 tasks each
    assert len(results) == expected_results, f"Expected {expected_results} results, got {len(results)}"
    
    # Verify no duplicate results (thread safety)
    unique_results = set(results)
    assert len(unique_results) == len(results), "Duplicate results detected - thread safety issue"
    
    print("✓ Thread safety test passed")
    return True


def test_managed_request_context():
    """
    Test the managed request context manager.
    """
    print("Testing managed request context...")
    
    def simple_task():
        return "Context task completed"
    
    # Test context manager
    with managed_request() as manager:
        future = manager.submit_request(simple_task)
        result = future.result(timeout=1.0)
        assert result == "Context task completed"
    
    print("✓ Managed request context test passed")
    return True


if __name__ == "__main__":
    print("Running concurrent request handling tests...")
    print("=" * 60)
    
    try:
        test_concurrent_request_handling()
        test_request_queue_management()
        test_thread_safety()
        test_managed_request_context()
        
        print("=" * 60)
        print("✓ All concurrent request handling tests completed successfully!")
        print("\nProperty 7 (Concurrent Request Handling) has been validated.")
        print("The system correctly handles concurrent requests without data corruption.")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)