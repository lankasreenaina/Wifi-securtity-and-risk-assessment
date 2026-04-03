import joblib
import pandas as pd
import os
import numpy as np

class RiskPredictor:
    def __init__(self, rf_model_path="ai_model/risk_model.joblib", if_model_path="ai_model/anomaly_model.joblib"):
        self.rf_model_path = rf_model_path
        self.if_model_path = if_model_path
        
        self.rf_model = joblib.load(self.rf_model_path) if os.path.exists(self.rf_model_path) else None
        self.if_model = joblib.load(self.if_model_path) if os.path.exists(self.if_model_path) else None

    def predict(self, features):
        """
        Predicts risk score and anomaly status.
        features: dictionary of features
        """
        if self.if_model is None:
            print("[!] Anomaly model not loaded. Returning fallback.")
            return 50, "UNKNOWN", False

        # 1. Anomaly Detection (Isolation Forest)
        prediction = self.if_model.predict(pd.DataFrame([features]))[0]
        is_anomaly = True if prediction == -1 else False
        
        # 2. Heuristic Risk Calculation (Grounded in Security Facts)
        # This replaces the "random" feel of the synthetic model
        enc_risk = {0: 90, 1: 80, 2: 50, 3: 5, 4: 0}.get(features.get('encryption_type', 3), 10)
        
        # Unauthorized device risk (5 points per unknown device, capped at 40)
        unk_risk = min(40, features.get('unknown_device_count', 0) * 5)
        
        # Attack surface risk (open ports: 2 points each, capped at 20)
        port_risk = min(20, features.get('open_ports_count', 0) * 2)
        
        # Unusual activity risk (Ports 21, 23, 445 etc)
        unusual_risk = 25 if features.get('unusual_ports', 0) == 1 else 0
        
        # Traffic anomaly weight
        # If anomaly is detected, we bump the risk significantly
        anomaly_weight = 30 if is_anomaly else 0
        
        raw_score = enc_risk + unk_risk + port_risk + unusual_risk + anomaly_weight
        
        # Consistency Check: If anomaly is NOT detected and security is decent, cap the risk
        if not is_anomaly and enc_risk <= 5:
            raw_score = min(40, raw_score)

        risk_score = int(np.clip(raw_score, 0, 100))
        
        # 3. Determine Risk Level
        if risk_score < 30:
            level = "LOW"
        elif risk_score < 60:
            level = "MEDIUM"
        elif risk_score < 85:
            level = "HIGH"
        else:
            level = "CRITICAL"
            
        return risk_score, level, is_anomaly

if __name__ == "__main__":
    predictor = RiskPredictor()
    # Test case: Normal
    normal_features = {
        "encryption_type": 3, "device_count": 5, "unknown_device_count": 0,
        "open_ports_count": 2, "traffic_level": 30, "traffic_peak": 10, "unusual_ports": 0
    }
    # Test case: Anomaly
    anomaly_features = {
        "encryption_type": 0, "device_count": 50, "unknown_device_count": 15,
        "open_ports_count": 40, "traffic_level": 90, "traffic_peak": 95, "unusual_ports": 1
    }
    
    for name, feat in [("Normal", normal_features), ("Anomaly", anomaly_features)]:
        score, level, anomaly = predictor.predict(feat)
        print(f"Scenario: {name}")
        print(f"  Risk Score: {score}/100 ({level})")
        print(f"  Anomaly Detected: {anomaly}")
        print("-" * 20)

