from ai_model.feature_encoder import FeatureEncoder
from ai_model.rule_engine import RuleEngine
from ai_model.ml_engine import MLEngine

class HybridRiskScorer:
    def __init__(self):
        self.ml_engine = MLEngine()
        self.rule_engine = RuleEngine()

    def generate_recommendations(self, wifi_data, network_data):
        recs = []
        encryption = str(wifi_data.get('encryption', '')).upper()
        auth = str(wifi_data.get('authentication', '')).upper()
        
        # Wi-Fi Recommends
        if "WPA3" not in auth and "SAE" not in auth:
            if "WPA2" in auth:
                recs.append("Upgrade to WPA3 for better security against dictionary attacks.")
            else:
                recs.append("CRITICAL: Network is OPEN or using WEAK encryption. Upgrade to WPA2/WPA3 immediately.")
                
        # Network Recommends
        ports_obj = network_data.get('port_scan_results', {})
        open_ports = ports_obj.get('open_ports', 0)
        risky_ports = ports_obj.get('risky_ports', [])
        unknown_devices = network_data.get('unknown_devices', 0)
        device_count = network_data.get('device_count', 0)
        
        if unknown_devices > 0:
            recs.append(f"Remove or investigate {unknown_devices} unknown devices.")
            
        if open_ports > 0:
            if risky_ports:
                recs.append(f"CRITICAL: Disable vulnerable ports immediately: {', '.join(risky_ports)}")
            else:
                recs.append("Review open ports on the gateway. Disable unused services (Telnet/HTTP).")
                
        if device_count > 6:
            recs.append("High number of active devices. Consider limiting connections or implementing MAC filtering.")
            
        if not recs:
            recs.append("Network configuration appears secure. No immediate action required.")
            
        return recs

    def compute_risk(self, wifi_data, network_data):
        encoded_features = FeatureEncoder.extract_features(wifi_data, network_data)
        
        # Predict via ML
        ml_score = self.ml_engine.predict_risk(encoded_features)
        
        # Calculate via Rules
        rule_score = self.rule_engine.calculate_risk(wifi_data, network_data)
        
        # Hybrid Approach: Blend both
        # 60% weight to ML, 40% to rigid rules
        final_score = (ml_score * 0.6) + (rule_score * 0.4)
        final_score = int(min(100, max(0, final_score)))
        
        if final_score >= 70:
            level = "HIGH"
        elif final_score >= 40:
            level = "MEDIUM"
        else:
            level = "LOW"
            
        recs = self.generate_recommendations(wifi_data, network_data)
        
        return {
            "score": final_score,
            "level": level,
            "components": {
                "ml_score": float(round(ml_score, 2)),
                "rule_score": float(round(rule_score, 2)),
            },
            "recommendations": recs
        }

if __name__ == "__main__":
    wifi_test = {"authentication": "WPA2-Personal", "encryption": "CCMP"}
    net_test = {"unknown_devices": 2, "device_count": 8, "port_scan_results": {"open_ports": 2, "risky_ports": ["23 (Telnet)"]}}
    
    scorer = HybridRiskScorer()
    res = scorer.compute_risk(wifi_test, net_test)
    import json
    print(json.dumps(res, indent=4))
