import pandas as pd
import numpy as np
import os

def generate_synthetic_dataset(output_file="data/training_dataset.csv", num_samples=1000):
    """
    Generates a synthetic dataset for Wi-Fi risk scoring and anomaly detection.
    Features:
    - encryption_type: 0 (Open), 1 (WEP), 2 (WPA1), 3 (WPA2), 4 (WPA3)
    - device_count: 1 to 30
    - unknown_device_count: 0 to 10
    - open_ports_count: 0 to 20
    - traffic_level: 0 (Low) to 100 (High)
    - traffic_peak: 0 to 100 (Magnitude of spikes)
    - unusual_ports: 0 (No), 1 (Yes)
    
    Target:
    - risk_score: 0 to 100
    """
    np.random.seed(42)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    data = []
    for i in range(num_samples):
        # Determine if this sample is an anomaly (e.g., 5% probability)
        is_anomaly = np.random.random() < 0.05
        
        if is_anomaly:
            # Anomalous features
            enc = np.random.randint(0, 2) # Likely open or WEP
            dev_count = np.random.randint(40, 100) # Unusually high
            unk_dev = np.random.randint(20, 50)
            open_ports = np.random.randint(30, 100)
            traffic = np.random.randint(80, 101)
            traffic_peak = np.random.randint(80, 101)
            unusual_ports = 1
        else:
            # Normal features
            enc = np.random.randint(2, 5) # Likely WPA2 or WPA3
            dev_count = np.random.randint(1, 21)
            unk_dev = np.random.randint(0, min(dev_count, 3))
            open_ports = np.random.randint(0, 11)
            traffic = np.random.randint(10, 60)
            traffic_peak = np.random.randint(0, 40)
            unusual_ports = 0

        # Risk Score Logic (Weighted sum with some noise)
        enc_risk = {0: 90, 1: 80, 2: 60, 3: 10, 4: 0}[enc]
        unk_risk = unk_dev * 5
        port_risk = open_ports * 2
        dev_risk = max(0, dev_count - 10) * 1
        traffic_risk = (traffic / 100) * 10
        peak_risk = (traffic_peak / 100) * 10
        unusual_risk = unusual_ports * 20

        total_risk = enc_risk + unk_risk + port_risk + dev_risk + traffic_risk + peak_risk + unusual_risk
        total_risk += np.random.normal(0, 5)
        
        risk_score = int(np.clip(total_risk, 0, 100))

        data.append({
            "encryption_type": enc,
            "device_count": dev_count,
            "unknown_device_count": unk_dev,
            "open_ports_count": open_ports,
            "traffic_level": traffic,
            "traffic_peak": traffic_peak,
            "unusual_ports": unusual_ports,
            "risk_score": risk_score
        })

    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    print(f"[+] Generated {num_samples} samples and saved to {output_file}")


if __name__ == "__main__":
    generate_synthetic_dataset()
    bitumen_df = pd.read_csv("data/training_dataset.csv")
    print(bitumen_df.head())
