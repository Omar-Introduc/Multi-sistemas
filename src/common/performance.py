import time
import threading
import functools

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
        self.lock = threading.Lock()

    def record(self, name, duration):
        with self.lock:
            if name not in self.metrics:
                self.metrics[name] = {'count': 0, 'total_time': 0, 'max': 0}

            self.metrics[name]['count'] += 1
            self.metrics[name]['total_time'] += duration
            if duration > self.metrics[name]['max']:
                self.metrics[name]['max'] = duration

    def get_stats(self):
        with self.lock:
            stats = {}
            for name, data in self.metrics.items():
                avg = data['total_time'] / data['count'] if data['count'] > 0 else 0
                stats[name] = {
                    'avg_ms': avg * 1000,
                    'max_ms': data['max'] * 1000,
                    'count': data['count']
                }
            return stats

monitor = PerformanceMonitor()

def time_execution(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        monitor.record(func.__name__, duration)
        return result
    return wrapper
