import asyncio
import json
import os
from datetime import datetime
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from scanner.wifi_metadata_collector import WifiMetadataCollector
from scanner.network_scanner import NetworkScanner
from ai_model.hybrid_risk import HybridRiskScorer

app = FastAPI(title="Wi-Fi Security API")

# Allow React Frontend Connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the modules
wifi_collector = WifiMetadataCollector()
net_scanner = NetworkScanner()
ai_scorer = HybridRiskScorer()

# State holder for real-time frontend
class State:
    latest_scan = {}
    history = []
    demo_mode = None  # None, "scenario_1", "scenario_2"

state = State()

def get_demo_data(scenario):
    if scenario == "scenario_1":
        # WPA2, Many devices, Open ports -> HIGH risk
        wifi = {"authentication": "WPA2-Personal", "encryption": "CCMP", "ssid": "Demo_Hostel_Net", "signal_strength": 80}
        net = {"device_count": 25, "unknown_devices": 10, "port_scan_results": {"open_ports": 5, "risky_ports": ["21 (FTP)", "23 (Telnet)", "80 (HTTP)"]}}
        devices = [{"ip": f"192.168.1.{i}", "mac": "00:00:00:00:AA:BB", "vendor": "Unknown" if i % 2 == 0 else "Apple", "is_unknown": i % 2 == 0} for i in range(10, 35)]
        net['devices'] = devices
    else:
        # WPA3, Fewer devices, Closed ports -> LOW risk
        wifi = {"authentication": "WPA3-Personal", "encryption": "CCMP", "ssid": "Demo_Secure_Net", "signal_strength": 95}
        net = {"device_count": 4, "unknown_devices": 0, "port_scan_results": {"open_ports": 0, "risky_ports": []}}
        devices = [{"ip": f"192.168.1.{i}", "mac": "00:00:00:00:AA:BB", "vendor": "Known Device", "is_unknown": False} for i in range(2, 6)]
        net['devices'] = devices
        
    risk_info = ai_scorer.compute_risk(wifi, net)

    return {
        "timestamp": datetime.now().isoformat(),
        "wifi": wifi,
        "network": net,
        "risk": risk_info,
        "scenario": scenario
    }

def run_actual_scan():
    wifi_data = wifi_collector.collect_metadata()
    net_data = net_scanner.run_full_scan()
    risk_info = ai_scorer.compute_risk(wifi_data, net_data)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "wifi": wifi_data,
        "network": net_data,
        "risk": risk_info
    }

async def background_scanner_loop():
    """Continuously scans the network every 7 seconds."""
    history_file = os.path.join("data", "wifi_history.json")
    
    # Load past history on startup
    if os.path.exists(history_file):
        try:
            with open(history_file, "r") as f:
                state.history = json.load(f)[-50:] # Keep last 50
        except Exception:
            pass
            
    while True:
        try:
            if state.demo_mode:
                scan_res = get_demo_data(state.demo_mode)
            else:
                scan_res = run_actual_scan()
                
            state.latest_scan = scan_res
            state.history.append({
                "timestamp": scan_res["timestamp"],
                "risk_score": scan_res["risk"]["score"],
                "device_count": scan_res["network"]["device_count"]
            })
            
            # Keep history truncated
            if len(state.history) > 50:
                state.history = state.history[-50:]
                
            with open(history_file, 'w') as f:
                json.dump(state.history, f)
                
        except Exception as e:
            print(f"[!] Background Scan Error: {e}")
            
        await asyncio.sleep(7)

@app.on_event("startup")
async def startup_event():
    # Attempt to load the ML model into memory instantly
    _ = ai_scorer.compute_risk({}, {})
    asyncio.create_task(background_scanner_loop())

@app.get("/scan")
def get_latest_scan():
    # Defaults if scanner hasn't run yet
    if not state.latest_scan:
        return {"status": "Initializing scanners... Try again in a few seconds."}
    return state.latest_scan

@app.get("/risk")
def get_risk_info():
    if not state.latest_scan: return {"score": 0, "level": "UNKNOWN"}
    return state.latest_scan.get("risk", {})

@app.get("/devices")
def get_devices():
    if not state.latest_scan: return []
    return state.latest_scan.get("network", {}).get("devices", [])

@app.get("/ports")
def get_ports():
    if not state.latest_scan: return {}
    return state.latest_scan.get("network", {}).get("port_scan_results", {})

@app.get("/history")
def get_history():
    return state.history

@app.get("/report")
def get_report():
    if not state.latest_scan:
        return {"error": "No scan data available yet."}
    return {
        "latest_scan": state.latest_scan,
        "history": state.history
    }

class ScenarioRequest(BaseModel):
    mode: str

@app.post("/demo")
def set_demo_mode(req: ScenarioRequest):
    """mode: 'scenario_1', 'scenario_2', or 'real'"""
    if req.mode == "real":
        state.demo_mode = None
    elif req.mode in ["scenario_1", "scenario_2"]:
        state.demo_mode = req.mode
    else:
        return {"error": "Invalid mode"}
        
    return {"status": f"Mode set to {req.mode}. Wait ~7 seconds for next scan tick."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
