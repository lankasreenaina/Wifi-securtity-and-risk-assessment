class FeatureEncoder:
    """Encodes categorical text features into integers for Neural/ML evaluation."""
    
    @staticmethod
    def encode_encryption(encryption_text):
        """Maps encryption types to a numeric risk level (1 = Best, 5 = Worst)."""
        text = str(encryption_text).upper()
        
        # OWA/Open
        if "OPEN" in text or "NONE" in text:
            return 5
        # WEP (very weak)
        if "WEP" in text:
            return 4
        # WPA (weak)
        if "WPA" in text and "WPA2" not in text and "WPA3" not in text:
            return 3
        # WPA2 (standard)
        if "WPA2" in text:
            return 2
        # WPA3 (best)
        if "WPA3" in text or "CCMP" in text or "SAE" in text:
            return 1
            
        # Default unknown to standard
        return 2

    @staticmethod
    def extract_features(wifi_data, network_data):
        """Constructs the exact input required for the ML model."""
        encryption = FeatureEncoder.encode_encryption(wifi_data.get('authentication', 'WPA2-Personal'))
        device_count = network_data.get('device_count', 0)
        unknown_devices = network_data.get('unknown_devices', 0)
        
        # open ports might be a count or a dict from the scan output
        ports_obj = network_data.get('port_scan_results', {})
        open_ports = ports_obj.get('open_ports', 0)
        
        return {
            "encryption": encryption,
            "device_count": device_count,
            "unknown_devices": unknown_devices,
            "open_ports": open_ports
        }
