import time
import logging
import functools
import traceback
from typing import Callable, Any, Dict

import prometheus_client
import psutil
import os

class PerformanceMetrics:
    """
    Comprehensive performance monitoring and metrics collection utility.
    
    This class provides advanced performance tracking with Prometheus metrics
    for transaction ID validation, uniqueness checks, and system performance.
    """

    # Prometheus metrics registry
    _metrics_registry = prometheus_client.CollectorRegistry()

    # Transaction metrics
    _transaction_total = prometheus_client.Counter(
        'transactions_total', 
        'Total number of transactions processed', 
        registry=_metrics_registry
    )
    _transaction_rejected = prometheus_client.Counter(
        'transactions_rejected', 
        'Number of rejected transactions', 
        registry=_metrics_registry
    )
    _transaction_latency = prometheus_client.Histogram(
        'transaction_latency_seconds', 
        'Transaction processing latency', 
        registry=_metrics_registry
    )
    _uniqueness_check_duration = prometheus_client.Histogram(
        'uniqueness_check_duration_seconds', 
        'Duration of uniqueness checks', 
        registry=_metrics_registry
    )

    @classmethod
    def track_transaction(cls, transaction_id: str) -> Callable:
        """
        Decorator to track transaction performance and metrics.
        
        Args:
            transaction_id (str): Unique identifier for the transaction
        
        Returns:
            Callable: Decorated function with performance tracking
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                # Increment total transactions
                cls._transaction_total.inc()
                
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    # Track rejected transactions
                    cls._transaction_rejected.inc()
                    logging.error(f"Transaction {transaction_id} failed: {e}")
                    raise
                finally:
                    # Record transaction latency
                    latency = time.time() - start_time
                    cls._transaction_latency.observe(latency)
            return wrapper
        return decorator

    @classmethod
    def check_uniqueness(cls, func: Callable) -> Callable:
        """
        Decorator to track uniqueness check performance.
        
        Args:
            func (Callable): Function performing uniqueness check
        
        Returns:
            Callable: Decorated function with uniqueness check tracking
        """
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # Record uniqueness check duration
                duration = time.time() - start_time
                cls._uniqueness_check_duration.observe(duration)
        return wrapper

    @classmethod
    def get_system_metrics(cls) -> Dict[str, Any]:
        """
        Retrieve current system resource metrics.
        
        Returns:
            Dict[str, Any]: Comprehensive system performance metrics
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
            logging.error(f"Error retrieving system metrics: {e}")
            return {}

    @classmethod
    def export_metrics(cls) -> str:
        """
        Export Prometheus metrics as a string.
        
        Returns:
            str: Metrics in Prometheus text format
        """
        try:
            from prometheus_client import generate_latest
            metrics_str = generate_latest(cls._metrics_registry).decode('utf-8')
            return metrics_str
        except Exception as e:
            logging.error(f"Error exporting metrics: {e}")
            return ""