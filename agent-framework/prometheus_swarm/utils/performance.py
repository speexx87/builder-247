import time
import functools
import logging
import tracemalloc
import traceback
import psutil
import os
from typing import Callable, Any, Dict

class PerformanceMonitor:
    """
    A comprehensive performance monitoring utility for tracking 
    function execution time, memory usage, and system resources.
    """

    @staticmethod
    def trace_performance(logger: logging.Logger = None) -> Callable:
        """
        Decorator to trace performance metrics of a function.

        Args:
            logger (logging.Logger, optional): Logger to record performance metrics. 
                                               Defaults to None.

        Returns:
            Callable: Decorated function with performance tracing
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                # Start memory tracing
                tracemalloc.start()
                start_memory = tracemalloc.get_traced_memory()[0]
                
                # Start time tracking
                start_time = time.time()
                
                # Track CPU usage before function call
                process = psutil.Process(os.getpid())
                start_cpu = process.cpu_percent()

                try:
                    # Execute the function
                    result = func(*args, **kwargs)
                    
                    # Calculate metrics
                    end_time = time.time()
                    end_cpu = process.cpu_percent()
                    
                    # Calculate memory usage
                    end_memory = tracemalloc.get_traced_memory()[0]
                    memory_diff = end_memory - start_memory
                    
                    # Performance metrics
                    metrics = {
                        'function_name': func.__name__,
                        'execution_time_ms': round((end_time - start_time) * 1000, 2),
                        'memory_usage_bytes': memory_diff,
                        'cpu_usage_percent': round(end_cpu, 2)
                    }
                    
                    # Log metrics if logger is provided
                    if logger:
                        logger.info(f"Performance Metrics for {func.__name__}: {metrics}")
                    
                    return result
                
                except Exception as e:
                    # Log and re-raise any exceptions
                    if logger:
                        logger.error(f"Error in {func.__name__}: {str(e)}")
                        logger.error(traceback.format_exc())
                    raise
                
                finally:
                    # Stop memory tracing
                    tracemalloc.stop()
            
            return wrapper
        return decorator
    
    @staticmethod
    def get_system_metrics() -> Dict[str, Any]:
        """
        Retrieve current system resource metrics.

        Returns:
            Dict[str, Any]: A dictionary of system metrics
        """
        try:
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_usage': {
                    'total': psutil.virtual_memory().total,
                    'available': psutil.virtual_memory().available,
                    'percent': psutil.virtual_memory().percent
                },
                'disk_usage': {
                    'total': psutil.disk_usage('/').total,
                    'used': psutil.disk_usage('/').used,
                    'percent': psutil.disk_usage('/').percent
                }
            }
        except Exception as e:
            logging.error(f"Error retrieving system metrics: {str(e)}")
            return {}