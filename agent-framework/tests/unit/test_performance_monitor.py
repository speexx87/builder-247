import pytest
import time
import logging
from prometheus_swarm.utils.performance import PerformanceMonitor

# Configure a basic logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestPerformanceMonitor:
    @PerformanceMonitor.trace_performance(logger=logger)
    def _sample_function(self, duration=0.1):
        """A sample function to test performance tracing."""
        time.sleep(duration)
        return "Test Complete"

    def test_trace_performance(self):
        """Test the performance tracing decorator."""
        result = self._sample_function()
        assert result == "Test Complete"

    def test_system_metrics(self):
        """Test retrieving system metrics."""
        metrics = PerformanceMonitor.get_system_metrics()
        
        # Validate system metrics structure
        assert 'cpu_percent' in metrics
        assert 'memory_usage' in metrics
        assert 'disk_usage' in metrics
        
        # Validate memory metrics
        assert 'total' in metrics['memory_usage']
        assert 'available' in metrics['memory_usage']
        assert 'percent' in metrics['memory_usage']
        
        # Validate disk metrics
        assert 'total' in metrics['disk_usage']
        assert 'used' in metrics['disk_usage']
        assert 'percent' in metrics['disk_usage']
        
        # Validate values are within expected ranges
        assert 0 <= metrics['cpu_percent'] <= 100
        assert 0 <= metrics['memory_usage']['percent'] <= 100
        assert 0 <= metrics['disk_usage']['percent'] <= 100

    def test_performance_metric_values(self):
        """Test the performance metrics of the traced function."""
        result = self._sample_function(duration=0.2)
        assert result == "Test Complete"

    def test_trace_performance_with_exceptions(self):
        """Test performance tracing with an exception."""
        @PerformanceMonitor.trace_performance(logger=logger)
        def _error_function():
            raise ValueError("Test Exception")
        
        with pytest.raises(ValueError):
            _error_function()