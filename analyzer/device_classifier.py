import pandas as pd
import os

class DeviceClassifier:
    def __init__(self, input_file="data/processed_data.csv"):
        self.input_file = input_file

    def classify_devices(self):
        """Classifies devices based on vendor names and open ports."""
        if not os.path.exists(self.input_file):
            print(f"[!] Input file {self.input_file} not found.")
            return []

        df = pd.read_csv(self.input_file)
        if 'DeviceType' not in df.columns:
            df['DeviceType'] = 'Unknown'
        classifications = []

        for index, row in df.iterrows():
            vendor = str(row['Vendor']).lower()
            ports = str(row['OpenPorts']).split()
            
            device_type = "Unknown"
            
            # Simple keyword-based classification
            if any(k in vendor for k in ['apple', 'samsung', 'huawei', 'google', 'xiaomi']):
                if '62078' in ports or not ports: # Common mobile ports or no ports open
                    device_type = "Smartphone"
                else:
                    device_type = "Laptop"
            elif any(k in vendor for k in ['intel', 'dell', 'hp', 'lenovo', 'asus', 'microsoft']):
                device_type = "Laptop"
            elif any(k in vendor for k in ['tp-link', 'd-link', 'netgear', 'cisco', 'asus', 'huawei']):
                if '80' in ports or '443' in ports or '53' in ports:
                    device_type = "Router"
            elif any(k in vendor for k in ['raspberry', 'espressif', 'amazon', 'roku', 'sonos', 'tuya']):
                device_type = "IoT device"
            
            # Additional logic based on ports
            if device_type == "Unknown":
                if '22' in ports or '3389' in ports or '5900' in ports:
                    device_type = "Laptop" # Likely a PC with remote access
                elif '80' in ports or '443' in ports:
                    device_type = "IoT device" # Web interface common in IoT
            
            classifications.append(device_type)

        df['DeviceType'] = classifications
        df.to_csv(self.input_file, index=False)
        print(f"[+] Device classification complete. Updated {self.input_file}")
        return df.to_dict('records')

if __name__ == "__main__":
    classifier = DeviceClassifier()
    classifier.classify_devices()
