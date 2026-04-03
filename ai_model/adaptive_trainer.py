import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import os
import time
from scanner.wifi_metadata_collector import WifiMetadataCollector
from scanner.network_scanner import NetworkScanner
from scanner.traffic_monitor import TrafficMonitor

class AdaptiveTrainer:
    def __init__(self, baseline_file="data/host_baseline.csv", model_path="ai_model/anomaly_model.joblib"):
        self.baseline_file = baseline_file
        self.model_path = model_path
        os.makedirs(os.path.dirname(self.baseline_file), exist_ok=True)

    def capture_baseline(self, duration_seconds=60, sample_interval=5):
        """
        Captures real-time network snapshots over a duration to build a local baseline.
        """
        print(f"[*] Starting Baseline Capture for {duration_seconds} seconds...")
        
        wifi_collector = WifiMetadataCollector()
        net_scanner = NetworkScanner()
        traffic_monitor = TrafficMonitor(interval=2)
        
        baseline_data = []
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            # 1. Collect features
            wifi_data = wifi_collector.collect_metadata()
            primary_wifi = wifi_data[0] if wifi_data else {}
            
            traffic, peak = traffic_monitor.get_traffic_metrics()
            net_data = net_scanner.scan_network()
            
            # Map encryption (reusing existing logic)
            enc_map = {"OPEN": 0, "WEP": 1, "WPA": 2, "WPA2": 3, "WPA3": 4, "NONE": 0}
            enc_str = str(primary_wifi.get('Authentication', 'Unknown')).upper()
            enc_type = 3
            for k, v in enc_map.items():
                if k in enc_str:
                    enc_type = v
                    break

            features = {
                "encryption_type": enc_type,
                "device_count": len(net_data),
                "unknown_device_count": len([d for d in net_data if d['Vendor'] == 'Unknown']),
                "open_ports_count": sum([len(d['OpenPorts'].split()) for d in net_data]),
                "traffic_level": traffic,
                "traffic_peak": peak,
                "unusual_ports": 0 # Baseline assumes normal behavior
            }
            
            baseline_data.append(features)
            print(f"[+] Sample {len(baseline_data)} captured. {int(duration_seconds - (time.time() - start_time))}s remaining.")
            time.sleep(max(0, sample_interval - 2)) # Account for traffic monitor sleep

        df = pd.DataFrame(baseline_data)
        df.to_csv(self.baseline_file, index=False)
        print(f"[+] Baseline data saved to {self.baseline_file}")
        return df

    def train_on_baseline(self):
        """
        Trains the Isolation Forest specifically on the captured host baseline.
        """
        if not os.path.exists(self.baseline_file):
            print("[!] No baseline data found. Capture it first.")
            return

        print("[*] Training Anomaly Detector on host baseline...")
        df = pd.read_csv(self.baseline_file)
        
        # Isolation Forest needs enough samples to estimate contamination
        # If baseline is small, we use a very low contamination
        model = IsolationForest(contamination=0.01, random_state=42)
        model.fit(df)
        
        joblib.dump(model, self.model_path)
        print(f"[+] Local Anomaly Model saved to {self.model_path}")

if __name__ == "__main__":
    trainer = AdaptiveTrainer()
    # Quick 30s baseline for testing
    trainer.capture_baseline(duration_seconds=30, sample_interval=5)
    trainer.train_on_baseline()
