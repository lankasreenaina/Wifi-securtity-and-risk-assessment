class RuleEngine:
    """Implements mandatory rule-based Risk Calculation."""
    
    @staticmethod
    def calculate_risk(wifi_data, network_data):
        risk = 0
        
        # Wi-Fi Features
        encryption = str(wifi_data.get('authentication', '')).upper()
        if "WPA2" in encryption and "WPA3" not in encryption and "SAE" not in encryption:
            risk += 3
        if "OPEN" in encryption or "NONE" in encryption:
            risk += 5
            
        # Network Features
        unknown_devices = network_data.get('unknown_devices', 0)
        device_count = network_data.get('device_count', 0)
        
        ports_obj = network_data.get('port_scan_results', {})
        open_ports = ports_obj.get('open_ports', 0)
        risky_ports = ports_obj.get('risky_ports', [])

        if unknown_devices > 0:
            risk += 3
        if open_ports > 0:
            risk += 2
        # Penalize explicitly for risky vulnerable ports (21, 23)
        if len(risky_ports) > 0:
            risk += 5
            
        if device_count > 6:
            risk += 2
            
        # Multiply by 5 for a 0-100 baseline stretch
        # Base max score via rules is around 20 -> 100
        normalized_risk = min(100, risk * 5)
        
        return normalized_risk
