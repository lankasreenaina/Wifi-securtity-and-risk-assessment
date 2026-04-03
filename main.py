import os
import sys
import pandas as pd
from scanner.wifi_metadata_collector import WifiMetadataCollector
from scanner.network_scanner import NetworkScanner
from scanner.traffic_monitor import TrafficMonitor
from analyzer.device_classifier import DeviceClassifier
from analyzer.misconfiguration_detector import MisconfigurationDetector
from ai_model.dataset_generator import generate_synthetic_dataset
from ai_model.train_model import RiskModelTrainer
from ai_model.risk_predictor import RiskPredictor
from recommendations.security_advisor import SecurityAdvisor

def run_pipeline():
    print("="*50)
    print("AI-Assisted Wi-Fi Security & Risk Assessment Prototype")
    print("="*50)

    # 1. Setup AI Model (if not exists)
    if not os.path.exists("ai_model/risk_model.joblib"):
        print("[*] Initializing AI Model...")
        generate_synthetic_dataset()
        trainer = RiskModelTrainer()
        trainer.train()

    # 2. Data Collection
    print("\n--- PHASE 1: Data Collection ---")
    wifi_collector = WifiMetadataCollector()
    wifi_data = wifi_collector.collect_metadata()
    wifi_collector.save_to_csv(wifi_data)

    traffic_monitor = TrafficMonitor(interval=2)
    traffic, peak = traffic_monitor.get_traffic_metrics()

    net_scanner = NetworkScanner()
    net_data = net_scanner.scan_network()
    net_scanner.save_to_csv(net_data)

    # 3. Analysis
    print("\n--- PHASE 2: Analysis & Classification ---")
    classifier = DeviceClassifier()
    classifier.classify_devices()

    detector = MisconfigurationDetector()
    vulnerabilities = detector.detect_vulnerabilities()
    print(f"[+] Detected {len(vulnerabilities)} vulnerabilities/misconfigurations.")

    # 4. Risk Prediction
    print("\n--- PHASE 3: AI Risk Prediction ---")
    predictor = RiskPredictor()
    
    # Extract features for prediction
    primary_wifi = wifi_data[0] if wifi_data else {}
    enc_map = {"OPEN": 0, "WEP": 1, "WPA": 2, "WPA2": 3, "WPA3": 4, "NONE": 0}
    
    enc_str = str(primary_wifi.get('Authentication', 'Unknown')).upper()
    enc_type = 3 # Default WPA2
    for k, v in enc_map.items():
        if k in enc_str:
            enc_type = v
            break

    # Dynamic features - now using real data
    features = {
        "encryption_type": enc_type,
        "device_count": len(net_data),
        "unknown_device_count": len([d for d in net_data if d['Vendor'] == 'Unknown']),
        "open_ports_count": sum([len(d['OpenPorts'].split()) for d in net_data]),
        "traffic_level": traffic,
        "traffic_peak": peak,
        "unusual_ports": 1 if any(v['Type'] == 'Insecure Port Open' for v in vulnerabilities) else 0
    }
    
    risk_score, risk_level, is_anomaly = predictor.predict(features)
    print(f"[!] Predicted Network Risk Score: {risk_score}/100")
    print(f"[!] Risk Level: {risk_level}")
    print(f"[!] Anomaly Detected: {'YES' if is_anomaly else 'NO'}")

    # 5. Recommendations
    print("\n--- PHASE 4: Security Recommendations ---")
    advisor = SecurityAdvisor()
    recommendations = advisor.generate_recommendations(vulnerabilities)
    for rec in recommendations:
        print(f"[{rec['Severity']}] {rec['Vulnerability']}: {rec['Recommendation']}")

    print("\n" + "="*50)
    print("Pipeline Complete. Run 'streamlit run dashboard/dashboard.py' to view results.")
    print("="*50)

def demonstrate_scenarios():
    """Simulates Scenario 1 (High Risk) vs Scenario 2 (Low Risk)."""
    print("\n" + "#"*50)
    print("DEMONSTRATION: MEASURABLE SECURITY IMPROVEMENT & ANOMALY DETECTION")
    print("#"*50)
    
    predictor = RiskPredictor()

    # Scenario 1: Weak Security + Anomaly
    s1_features = {
        "encryption_type": 1, 
        "device_count": 60,
        "unknown_device_count": 20,
        "open_ports_count": 50,
        "traffic_level": 90,
        "traffic_peak": 95,
        "unusual_ports": 1
    }
    score1, level1, anomaly1 = predictor.predict(s1_features)
    
    # Scenario 2: Improved Security
    s2_features = {
        "encryption_type": 4, 
        "device_count": 5,
        "unknown_device_count": 0,
        "open_ports_count": 1,
        "traffic_level": 20,
        "traffic_peak": 10,
        "unusual_ports": 0
    }
    score2, level2, anomaly2 = predictor.predict(s2_features)

    print(f"\nScenario 1: Weak Configuration & Anomaly Presence")
    print(f"Outcome: Risk Score = {score1} ({level1}) | Anomaly = {anomaly1}")
    
    print(f"\nScenario 2: Secure Configuration & Normal Behavior")
    print(f"Outcome: Risk Score = {score2} ({level2}) | Anomaly = {anomaly2}")
    
    improvement = score1 - score2
    print(f"\n[+] Measurable Security Improvement: {improvement} points reduction in risk score.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AI Wi-Fi Security & Risk Assessment")
    parser.add_argument("--demo", action="store_true", help="Run demonstration scenarios")
    parser.add_argument("--baseline", action="store_true", help="Capture real-world network baseline and calibrate AI")
    
    args = parser.parse_args()
    
    if args.baseline:
        from ai_model.adaptive_trainer import AdaptiveTrainer
        trainer = AdaptiveTrainer()
        trainer.capture_baseline(duration_seconds=60)
        trainer.train_on_baseline()
        print("[+] AI Calibration Complete. Run again without --baseline to start assessment.")
    elif args.demo:
        demonstrate_scenarios()
    else:
        run_pipeline()
        demonstrate_scenarios()
