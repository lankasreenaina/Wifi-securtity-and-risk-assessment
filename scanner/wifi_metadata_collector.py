import subprocess
import os
import re
import json
from datetime import datetime

class WifiMetadataCollector:
    def __init__(self, log_dir="data"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.history_file = os.path.join(self.log_dir, "wifi_history.json")

    def collect_metadata(self):
        """Collects Wi-Fi metadata for the active interface and nearby networks."""
        try:
            # 1. Get active interface details
            iface_output = subprocess.check_output(["netsh", "wlan", "show", "interfaces"], 
                                                 stderr=subprocess.STDOUT, 
                                                 universal_newlines=True)
            active_info = self._get_active_interface_details(iface_output)
            
            # If no active connection found, fallback to simulated data
            if not active_info or active_info.get("State") != "connected":
                return self._generate_simulated_data(reason="Not connected to Wi-Fi")
            
            # Format exactly as requested
            result = {
                "timestamp": datetime.now().isoformat(),
                "ssid": active_info.get("SSID", "Unknown"),
                "signal_strength": int(active_info.get("SignalStrength", 0)),
                "authentication": active_info.get("Authentication", "Open"),
                "encryption": active_info.get("Encryption", "None"),
                "channel": int(active_info.get("Channel", 0)),
                "bssid": active_info.get("BSSID", "00:00:00:00:00:00")
            }
            
            return result
        except Exception as e:
            return self._generate_simulated_data(reason=str(e))

    def _get_active_interface_details(self, output):
        """Parses output of 'netsh wlan show interfaces' for the active connection."""
        info = {"SSID": "Unknown", "BSSID": "00:00:00:00:00:00", "State": "Disconnected"}
        for line in output.split('\n'):
            line = line.strip()
            if "State" in line:
                info["State"] = line.split(":")[-1].strip()
            elif line.startswith("SSID") and "BSSID" not in line:
                info["SSID"] = line.split(":")[-1].strip()
            elif "BSSID" in line:
                info["BSSID"] = line.split(":")[-1].strip()
            elif "Authentication" in line:
                info["Authentication"] = line.split(":")[-1].strip()
            elif "Cipher" in line or "Encryption" in line:
                info["Encryption"] = line.split(":")[-1].strip()
            elif "Signal" in line:
                info["SignalStrength"] = line.split(":")[-1].strip().replace("%", "")
            elif "Channel" in line:
                info["Channel"] = line.split(":")[-1].strip()
        
        return info

    def _generate_simulated_data(self, reason="Failed"):
        """Simulates realistic data if netsh fails or returns nothing to prevent demo failure."""
        print(f"[!] Using simulated Wi-Fi data. Reason: {reason}")
        return {
            "timestamp": datetime.now().isoformat(),
            "ssid": "Hostel_WiFi",
            "signal_strength": 85,
            "authentication": "WPA2-Personal",
            "encryption": "CCMP",
            "channel": 6,
            "bssid": "00:1A:2B:3C:4D:5E",
            "is_simulated": True
        }

if __name__ == "__main__":
    collector = WifiMetadataCollector()
    data = collector.collect_metadata()
    print(json.dumps(data, indent=4))
