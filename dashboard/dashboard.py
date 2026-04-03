import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import json
import time

# Set page config
st.set_page_config(page_title="AI Wi-Fi Security Dashboard", layout="wide")

# Custom CSS for Premium Look
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.02);
    }
    h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .card {
        padding: 20px;
        border-radius: 15px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }
    .status-alert {
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        font-weight: bold;
    }
    .anomaly-critical { background-color: #ff4b4b; color: white; }
    .anomaly-none { background-color: #28a745; color: white; }
</style>
""", unsafe_allow_html=True)

from scanner.wifi_metadata_collector import WifiMetadataCollector
from scanner.network_scanner import NetworkScanner
from scanner.traffic_monitor import TrafficMonitor
from analyzer.device_classifier import DeviceClassifier
from analyzer.misconfiguration_detector import MisconfigurationDetector
from ai_model.risk_predictor import RiskPredictor
from ai_model.adaptive_trainer import AdaptiveTrainer
from recommendations.security_advisor import SecurityAdvisor

def save_assessment():
    """Saves current assessment to a JSON file."""
    data = {
        'risk_score': st.session_state.get('risk_score'),
        'risk_level': st.session_state.get('risk_level'),
        'is_anomaly': st.session_state.get('is_anomaly'),
        'recommendations': st.session_state.get('recommendations'),
        'last_scan': st.session_state.get('last_scan'),
        'features': st.session_state.get('features'),
        'traffic_history': st.session_state.get('traffic_history', [])
    }
    with open("data/last_assessment.json", "w") as f:
        json.dump(data, f)

def load_assessment():
    """Loads last assessment from JSON file into session state."""
    if os.path.exists("data/last_assessment.json"):
        try:
            with open("data/last_assessment.json", "r") as f:
                data = json.load(f)
            for k, v in data.items():
                if v is not None:
                    st.session_state[k] = v
        except Exception:
            pass

def get_last_scan_time():
    """Returns the last modified time of the network scans file."""
    if os.path.exists("data/network_scans.csv"):
        mtime = os.path.getmtime("data/network_scans.csv")
        return time.strftime("%H:%M:%S", time.localtime(mtime))
    return "Never"

def load_data():
    wifi_data = pd.DataFrame()
    device_data = pd.DataFrame()
    if os.path.exists("data/network_scans.csv"):
        try:
            wifi_data = pd.read_csv("data/network_scans.csv")
        except Exception:
            pass
    if os.path.exists("data/processed_data.csv"):
        try:
            device_data = pd.read_csv("data/processed_data.csv")
        except Exception:
            pass
    return wifi_data, device_data

# Initialize session state for persistent fields
if 'traffic_history' not in st.session_state:
    st.session_state['traffic_history'] = []
if 'last_scan' not in st.session_state:
    st.session_state['last_scan'] = None
if 'risk_score' not in st.session_state:
    st.session_state['risk_score'] = 0
if 'risk_level' not in st.session_state:
    st.session_state['risk_level'] = "IDLE"
if 'is_anomaly' not in st.session_state:
    st.session_state['is_anomaly'] = False
if 'recommendations' not in st.session_state:
    st.session_state['recommendations'] = []
if 'features' not in st.session_state:
    st.session_state['features'] = None
if 'available_networks_count' not in st.session_state:
    st.session_state['available_networks_count'] = 0

# Load persistent data only once on startup
if 'initialized' not in st.session_state:
    load_assessment()
    st.session_state['initialized'] = True

def run_calibration():
    with st.status("🎯 Calibrating AI Baseline...", expanded=True) as status:
        trainer = AdaptiveTrainer()
        interval = 3
        iterations = 10
        baseline_entries = []
        
        wifi_collector = WifiMetadataCollector()
        net_scanner = NetworkScanner()
        traffic_monitor = TrafficMonitor(interval=interval)
        
        for i in range(iterations):
            status.update(label=f"🎯 Calibration Phase: Capturing Sample {i+1}/{iterations}...")
            
            wifi_data = wifi_collector.collect_metadata()
            traffic, peak = traffic_monitor.get_traffic_metrics()
            net_data = net_scanner.scan_network()
            
            enc_map = {"OPEN": 0, "WEP": 1, "WPA": 2, "WPA2": 3, "WPA3": 4, "NONE": 0}
            enc_str = str(wifi_data[0].get('Authentication', 'Unknown')).upper() if wifi_data else "NONE"
            enc_type = 3
            for k, v in enc_map.items():
                if k in enc_str:
                    enc_type = v
                    break

            baseline_entries.append({
                "encryption_type": enc_type,
                "device_count": len(net_data),
                "unknown_device_count": len([d for d in net_data if d['Vendor'] == 'Unknown']),
                "open_ports_count": sum([len(d['OpenPorts'].split()) for d in net_data]),
                "traffic_level": traffic,
                "traffic_peak": peak,
                "unusual_ports": 0
            })

        pd.DataFrame(baseline_entries).to_csv(trainer.baseline_file, index=False)
        trainer.train_on_baseline()
        st.session_state['calibrated'] = True
        status.update(label="✅ AI Successfully Calibrated!", state="complete")
        time.sleep(2)
    st.rerun()

def run_dynamic_scan():
    with st.status("🚀 Running Dynamic Security Scan...", expanded=True) as status:
        # 1. Data Collection
        status.update(label="📡 Phase 1: Collecting Network Metadata...")
        wifi_collector = WifiMetadataCollector()
        wifi_data = wifi_collector.collect_metadata()
        wifi_collector.save_to_csv(wifi_data)

        status.update(label="📊 Phase 2: Monitoring Real-Time Traffic...")
        traffic_monitor = TrafficMonitor(interval=2)
        traffic, peak = traffic_monitor.get_traffic_metrics()
        
        # Update traffic history
        if 'traffic_history' in st.session_state:
            st.session_state['traffic_history'].append(traffic)
            if len(st.session_state['traffic_history']) > 20:
                st.session_state['traffic_history'].pop(0)
                
        status.update(label="🔍 Phase 3: Scanning Connected Devices...")
        net_scanner = NetworkScanner()
        net_data = net_scanner.scan_network()
        net_scanner.save_to_csv(net_data)

        # 2. Analysis
        status.update(label="🧠 Phase 4: AI Classification & Anomaly Detection...")
        classifier = DeviceClassifier()
        classifier.classify_devices()

        detector = MisconfigurationDetector()
        vulnerabilities = detector.detect_vulnerabilities()
        
        # 3. Risk Prediction
        status.update(label="🛡️ Phase 5: Risk Assessment Engine...")
        predictor = RiskPredictor()
        primary_wifi = wifi_data[0] if wifi_data else {}
        
        enc_map = {"OPEN": 0, "WEP": 1, "WPA": 2, "WPA2": 3, "WPA3": 4, "NONE": 0}
        enc_str = str(primary_wifi.get('Authentication', 'Unknown')).upper()
        enc_type = 3
        for k, v in enc_map.items():
            if k in enc_str:
                enc_type = v
                break

        unusual = 1 if any(v['Type'] == 'Insecure Port Open' for v in vulnerabilities) else 0

        features = {
            "encryption_type": enc_type,
            "device_count": len(net_data),
            "unknown_device_count": len([d for d in net_data if d['Vendor'] == 'Unknown']),
            "open_ports_count": sum([len(d['OpenPorts'].split()) for d in net_data]),
            "traffic_level": traffic,
            "traffic_peak": peak,
            "unusual_ports": unusual
        }
        
        risk_score, risk_level, is_anomaly = predictor.predict(features)
        
        # 4. Recommendations
        advisor = SecurityAdvisor()
        recommendations = advisor.generate_recommendations(vulnerabilities)
        
        # Store in session state
        st.session_state['risk_score'] = risk_score
        st.session_state['risk_level'] = risk_level
        st.session_state['is_anomaly'] = is_anomaly
        st.session_state['recommendations'] = recommendations
        st.session_state['last_scan'] = pd.Timestamp.now().strftime("%H:%M:%S")
        st.session_state['features'] = features
        st.session_state['available_networks_count'] = len(wifi_data)
        
        status.update(label="✅ Dynamic Analysis Complete!", state="complete")
        save_assessment()
        time.sleep(2)
    st.rerun()

# Sidebar Navigation
st.sidebar.markdown("# 🛡️ Security Center")
st.sidebar.divider()
page = st.sidebar.radio("Navigation", ["Overview", "Network Map", "AI Threat Intelligence"])

if st.sidebar.button("🎯 Calibrate AI Baseline"):
    run_calibration()

if st.sidebar.button("🚀 Trigger Real-time Scan"):
    run_dynamic_scan()

# Load Current Data
wifi_df, device_df = load_data()
last_scan_persistent = get_last_scan_time()

if page == "Overview":
    st.title("Network Security Intelligence Dashboard")
    
    if not st.session_state.get('calibrated') and not os.path.exists("ai_model/anomaly_model.joblib"):
        st.warning("⚠️ AI NOT CALIBRATED: Results may be inaccurate. Please click 'Calibrate AI Baseline' in the sidebar.")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    risk_score = st.session_state.get('risk_score', 0)
    risk_level = st.session_state.get('risk_level', "IDLE")
    is_anomaly = st.session_state.get('is_anomaly', False)
    
    with col1:
        st.metric("Total Risk Index", f"{risk_score}%", f"{risk_level}")
    with col2:
        available_net_count = st.session_state.get('available_networks_count', 0)
        st.metric("Available Networks", available_net_count, delta="Live" if st.session_state.get('live_mode') else None)
    with col3:
        live_host_count = st.session_state.get('live_host_count', len(device_df))
        st.metric("Connected Devices", live_host_count, delta="Live" if st.session_state.get('live_mode') else None)
    with col4:
        status = "CRITICAL" if is_anomaly else "NORMAL"
        st.metric("Anomaly Status", status, delta="Anomaly Detected" if is_anomaly else "Baseline Followed", delta_color="inverse" if is_anomaly else "normal")
    with col5:
        enc = wifi_df.iloc[0]['Authentication'] if not wifi_df.empty else "N/A"
        st.metric("Wireless Security", enc)

    st.divider()
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("📊 Real-time Traffic Throughput")
        if st.session_state['traffic_history']:
            history_df = pd.DataFrame(st.session_state['traffic_history'], columns=['Throughput %'])
            if len(history_df) > 1 and history_df['Throughput %'].nunique() == 1:
                history_df.iloc[-1, 0] += 0.01
            st.area_chart(history_df, use_container_width=True)
        else:
            st.info("No traffic data yet. Trigger a scan to start monitoring.")
        
        st.subheader("📱 Connected Device Inventory")
        if not device_df.empty:
            cols = ['IP', 'Vendor', 'MAC']
            if 'DeviceType' in device_df.columns:
                cols.insert(2, 'DeviceType')
            else:
                device_df['DeviceType'] = 'Unknown'
                cols.insert(2, 'DeviceType')
            st.dataframe(device_df[cols], use_container_width=True)
        else:
            st.info("Run a scan to see connected devices.")

    with c2:
        st.subheader("⚠️ AI Alerts & Insights")
        if is_anomaly:
            st.markdown('<div class="status-alert anomaly-critical">🔴 HIGH ANOMALY DETECTED: UNUSUAL TRAFFIC PATTERN</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-alert anomaly-none">🟢 SYSTEM BEHAVIOR NORMAL</div>', unsafe_allow_html=True)
            
        recs = st.session_state.get('recommendations', [])
        if recs:
            for rec in recs[:3]:
                with st.expander(f"📌 {rec['Vulnerability']}"):
                    st.write(rec['Recommendation'])
        else:
            st.success("No immediate threats found.")

elif page == "Network Map":
    st.title("Network Topology & Distribution")
    if not device_df.empty:
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.subheader("Device Types")
            counts = device_df['DeviceType'].value_counts()
            fig, ax = plt.subplots(facecolor='none')
            ax.pie(counts, labels=counts.index, autopct='%1.1f%%', textprops={'color':"w"})
            st.pyplot(fig)
        with col_m2:
            st.subheader("Vendor Distribution")
            st.bar_chart(device_df['Vendor'].value_counts())
    else:
        st.warning("No data available. Please run a scan.")

elif page == "AI Threat Intelligence":
    st.title("AI Risk Assessment Engine")
    if 'features' in st.session_state:
        feat = st.session_state['features']
        st.subheader("Model Input Vector")
        feat_df = pd.DataFrame([feat]).T
        feat_df.columns = ['Current Value']
        st.table(feat_df)
        
        st.subheader("Anomaly Detection Analysis")
        st.info("The Isolation Forest model flags data points that deviate significantly from historical patterns.")
        status = "ANOMALY" if st.session_state.get('is_anomaly') else "NORMAL"
        st.write(f"Result: **{status}**")
    else:
        st.info("Run a scan to generate AI insights.")

st.sidebar.divider()
display_time = st.session_state.get('last_scan', last_scan_persistent)
st.sidebar.info(f"🕒 Last scan: {display_time}")

live_mode = st.sidebar.toggle("📡 Live Monitoring Mode", value=st.session_state.get('live_mode', False))
st.session_state['live_mode'] = live_mode

if live_mode:
    st.sidebar.caption("🟢 Dashboard auto-refreshing...")
    if 'last_live_update' not in st.session_state or time.time() - st.session_state['last_live_update'] > 10:
        tm = TrafficMonitor(interval=1)
        t, _ = tm.get_traffic_metrics()
        st.session_state['traffic_history'].append(t)
        if len(st.session_state['traffic_history']) > 20:
            st.session_state['traffic_history'].pop(0)
            
        ns = NetworkScanner()
        st.session_state['live_host_count'] = ns.get_live_host_count()
        
        wc = WifiMetadataCollector()
        st.session_state['available_networks_count'] = wc.get_available_network_count()
        
        st.session_state['last_live_update'] = time.time()
        st.rerun()

st.sidebar.caption("AI-Powered Security Monitoring")
