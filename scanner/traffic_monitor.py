import psutil
import time
import pandas as pd

class TrafficMonitor:
    def __init__(self, interval=3):
        self.interval = interval

    def get_traffic_metrics(self):
        """
        Samples network IO for a short interval and returns traffic level and peak.
        Returns: (traffic_level, traffic_peak) normalized to 0-100.
        """
        print(f"[*] Sampling network traffic for {self.interval} seconds...")
        
        # Initial sample
        io1 = psutil.net_io_counters()
        time.sleep(self.interval)
        # Second sample
        io2 = psutil.net_io_counters()

        bytes_sent = io2.bytes_sent - io1.bytes_sent
        bytes_recv = io2.bytes_recv - io1.bytes_recv
        total_bytes = bytes_sent + bytes_recv
        
        # Normalize: Assuming 10MB/s (10*1024*1024 bytes) as '100' level for a 3s window
        # Adjust based on expected environment
        max_bytes_expected = 10 * 1024 * 1024 * self.interval 
        
        traffic_level = min(100, int((total_bytes / max_bytes_expected) * 100))
        
        # Peak calculation (simplified for this interval)
        # In a real app we'd sample more frequently, here we just add some jitter for demonstration
        traffic_peak = min(100, traffic_level + int(traffic_level * 0.2)) 
        
        print(f"[+] Measured traffic: {total_bytes / 1024:.2f} KB | Level: {traffic_level}%")
        return traffic_level, traffic_peak

if __name__ == "__main__":
    monitor = TrafficMonitor()
    level, peak = monitor.get_traffic_metrics()
    print(f"Level: {level}, Peak: {peak}")
