import pandas as pd
import os

class MisconfigurationDetector:
    def __init__(self, wifi_file="data/network_scans.csv", device_file="data/processed_data.csv"):
        self.wifi_file = wifi_file
        self.device_file = device_file

    def detect_vulnerabilities(self):
        vulnerabilities = []
        
        # 1. Analyze Wi-Fi Metadata
        if os.path.exists(self.wifi_file):
            wifi_df = pd.read_csv(self.wifi_file)
            for _, row in wifi_df.iterrows():
                auth = str(row['Authentication']).upper()
                encrypt = str(row['Encryption']).upper()
                
                if "WEP" in auth or "WEP" in encrypt:
                    vulnerabilities.append({
                        "Type": "Weak Encryption",
                        "Severity": "CRITICAL",
                        "Details": f"Access Point {row['SSID']} uses obsolete WEP encryption.",
                        "Feature": "encryption_type"
                    })
                elif "WPA" in auth and "WPA2" not in auth and "WPA3" not in auth:
                    vulnerabilities.append({
                        "Type": "Weak Encryption",
                        "Severity": "HIGH",
                        "Details": f"Access Point {row['SSID']} uses legacy WPA1 encryption.",
                        "Feature": "encryption_type"
                    })
                elif "OPEN" in auth or "NONE" in encrypt:
                    vulnerabilities.append({
                        "Type": "No Encryption",
                        "Severity": "CRITICAL",
                        "Details": f"Access Point {row['SSID']} is an open network.",
                        "Feature": "encryption_type"
                    })

        # 2. Analyze Device Discovery
        if os.path.exists(self.device_file):
            device_df = pd.read_csv(self.device_file)
            
            # Unknown Devices
            unknown_count = len(device_df[device_df['Vendor'] == 'Unknown'])
            if unknown_count > 0:
                vulnerabilities.append({
                    "Type": "Unknown Devices",
                    "Severity": "MEDIUM",
                    "Details": f"{unknown_count} devices with unknown vendors detected on the network.",
                    "Feature": "unknown_device_count"
                })

            # High Device Count
            if len(device_df) > 10:
                vulnerabilities.append({
                    "Type": "High Device Density",
                    "Severity": "LOW",
                    "Details": f"High number of devices ({len(device_df)}) connected to the network.",
                    "Feature": "device_count"
                })

            # Open Ports
            for _, row in device_df.iterrows():
                ports = str(row['OpenPorts']).split()
                if len(ports) > 3:
                    vulnerabilities.append({
                        "Type": "Too Many Open Ports",
                        "Severity": "MEDIUM",
                        "Details": f"Device {row['IP']} ({row['Vendor']}) has multiple open ports: {row['OpenPorts']}.",
                        "Feature": "open_ports_count"
                    })
                
                # Check for sensitive/dangerous ports
                dangerous_ports = {"21": "FTP", "23": "Telnet", "445": "SMB"}
                for p in ports:
                    if p in dangerous_ports:
                        vulnerabilities.append({
                            "Type": "Insecure Port Open",
                            "Severity": "HIGH",
                            "Details": f"Device {row['IP']} has insecure port {p} ({dangerous_ports[p]}) open.",
                            "Feature": "open_ports_count"
                        })

        return vulnerabilities

if __name__ == "__main__":
    detector = MisconfigurationDetector()
    vulns = detector.detect_vulnerabilities()
    for v in vulns:
        print(f"[{v['Severity']}] {v['Type']}: {v['Details']}")
