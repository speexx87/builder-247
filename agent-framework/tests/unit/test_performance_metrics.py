import pytest
import time
from src.performance_metrics import PerformanceMetrics

class TestPerformanceMetrics:
    def test_track_transaction_success(self):
        @PerformanceMetrics.track_transaction("test_transaction")
        def successful_transaction():
            return "Success"
        
        result = successful_transaction()
        assert result == "Success"

    def test_track_transaction_rejection(self):
        @PerformanceMetrics.track_transaction("test_reject")
        def rejected_transaction():
            raise ValueError("Rejected")
        
        with pytest.raises(ValueError):
            rejected_transaction()

    def test_uniqueness_check(self):
        @PerformanceMetrics.check_uniqueness
        def uniqueness_check():
            time.sleep(0.1)  # Simulate check
            return True
        
        result = uniqueness_check()
        assert result is True

    def test_system_metrics(self):
        metrics = PerformanceMetrics.get_system_metrics()
        
        assert 'cpu_percent' in metrics
        assert 'memory_usage' in metrics
        assert 'disk_usage' in metrics
        
        # Validate memory metrics
        memory_usage = metrics['memory_usage']
        assert 'total' in memory_usage
        assert 'available' in memory_usage
        assert 'percent' in memory_usage
        
        # Validate disk metrics
        disk_usage = metrics['disk_usage']
        assert 'total' in disk_usage
        assert 'used' in disk_usage
        assert 'percent' in disk_usage

    def test_metrics_export(self):
        metrics_export = PerformanceMetrics.export_metrics()
        assert isinstance(metrics_export, str)
        assert len(metrics_export) > 0