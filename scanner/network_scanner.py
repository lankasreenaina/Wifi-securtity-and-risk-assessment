import subprocess
import re
import socket
import nmap
import os
import json
from datetime import datetime

class NetworkScanner:
    def __init__(self, log_dir="data"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        # Nmap path for typical Windows install
        self.nmap_path = r"C:\Program Files (x86)\Nmap\nmap.exe"

    def get_default_gateway(self):
        """Extracts the default gateway IP dynamically using ipconfig."""
        try:
            output = subprocess.check_output("ipconfig", universal_newlines=True)
            for line in output.split('\n'):
                if "Default Gateway" in line or "Passerelle par d" in line: # Support varied locales
                    ip_match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", line)
                    if ip_match:
                        return ip_match.group(1)
            return None
        except Exception as e:
            print(f"[!] Warning: ipconfig failed ({e})")
            return None

    def discover_devices(self):
        """Uses arp -a to get active devices on the local subnet."""
        devices = []
        try:
            output = subprocess.check_output("arp -a", universal_newlines=True)
            pattern = re.compile(r"(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F:-]{17})")
            
            for match in pattern.finditer(output):
                ip, mac = match.groups()
                # Exclude broadcast/multicast IPs
                if ip.startswith(("224.", "239.", "255.", "169.254.")) or ip.endswith(".255"):
                    continue
                
                vendor = self._lookup_vendor(mac)
                devices.append({
                    "ip": ip,
                    "mac": mac,
                    "vendor": vendor,
                    "is_unknown": vendor == "Unknown"
                })
            
            if not devices:
                return self._generate_simulated_devices(reason="No devices found in ARP table.")
                
            return devices
                
        except Exception as e:
            return self._generate_simulated_devices(reason=f"ARP scan failed: {e}")

    def scan_router_ports(self, gateway_ip):
        """Uses Nmap to scan specific router ports for vulnerabilities."""
        if not gateway_ip:
            print("[!] No gateway IP provided for Nmap. Running fallback.")
            return {"open_ports": 2, "risky_ports": ["21 (FTP)", "23 (Telnet)"], "port_list": [21, 23, 80], "is_simulated": True}
            
        try:
            nm = nmap.PortScanner(nmap_search_path=(self.nmap_path,))
            nm.scan(hosts=gateway_ip, arguments='-F') 
            
            open_ports = []
            risky_ports = []
            
            risky_map = {
                21: "21 (FTP)",
                23: "23 (Telnet)",
                80: "80 (HTTP)",
                445: "445 (SMB)"
            }

            if gateway_ip in nm.all_hosts() and 'tcp' in nm[gateway_ip]:
                for port, info in nm[gateway_ip]['tcp'].items():
                    if info['state'] == 'open':
                        open_ports.append(port)
                        if port in risky_map:
                            risky_ports.append(risky_map[port])
            
            return {
                "open_ports": len(open_ports),
                "risky_ports": risky_ports,
                "port_list": open_ports,
                "is_simulated": False
            }
            
        except (nmap.PortScannerError, Exception) as e:
            print(f"[!] Nmap scan failed. Missing or Blocked? Error: {e}")
            return {"open_ports": 2, "risky_ports": ["21 (FTP)", "23 (Telnet)"], "port_list": [21, 23, 80], "is_simulated": True}

    def _lookup_vendor(self, mac):
        """A simple prefix lookup to determine known vs unknown vendors."""
        mac_prefix = mac[:8].upper().replace("-", ":")
        
        known_ouis = {
            "00:1A:2B": "Intel",
            "14:10:9F": "Apple",
            "48:4B:AA": "Samsung",
            "00:E0:4C": "Realtek",
            "DC:A6:32": "Raspberry Pi",
            "00:50:56": "VMware",
            "F4:F2:6D": "TP-Link"
        }
        
        if mac_prefix in known_ouis:
            return known_ouis[mac_prefix]
            
        return "Unknown"

    def _generate_simulated_devices(self, reason="Fallback"):
        """Simulated devices for Demo stability."""
        print(f"[!] Using simulated device data. Reason: {reason}")
        return [
            {"ip": "192.168.1.1", "mac": "00:1A:2B:3C:4D:5E", "vendor": "TP-Link", "is_unknown": False},
            {"ip": "192.168.1.5", "mac": "AA:BB:CC:DD:EE:FF", "vendor": "Apple", "is_unknown": False},
            {"ip": "192.168.1.10", "mac": "11:22:33:44:55:66", "vendor": "Samsung", "is_unknown": False},
            {"ip": "192.168.1.20", "mac": "FF:EE:DD:CC:BB:AA", "vendor": "Unknown", "is_unknown": True},
            {"ip": "192.168.1.25", "mac": "00:E0:4C:81:AA:FF", "vendor": "Unknown", "is_unknown": True}
        ]

    def run_full_scan(self):
        """Orchestrates the entire network scan."""
        gateway = self.get_default_gateway()
        devices = self.discover_devices()
        ports = self.scan_router_ports(gateway)
        
        unknown_count = sum(1 for d in devices if d['is_unknown'])
        
        return {
            "gateway_ip": gateway or "192.168.1.1 (Simulated)",
            "device_count": len(devices),
            "unknown_devices": unknown_count,
            "devices": devices,
            "port_scan_results": ports
        }

if __name__ == "__main__":
    scanner = NetworkScanner()
    data = scanner.run_full_scan()
    print(json.dumps(data, indent=4))
