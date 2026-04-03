import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

class MLEngine:
    def __init__(self, model_path="ai_model/random_forest_model.joblib"):
        self.model_path = model_path
        self.model = None
        self._load_or_train()

    def _load_or_train(self):
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
        else:
            self._train_synthetic_model()

    def _train_synthetic_model(self):
        print("[*] Training new Random Forest Model...")
        # Columns: encryption (1=Best, 5=Worst), device_count, unknown_devices, open_ports
        # Generate synthetic data
        np.random.seed(42)
        n_samples = 5000
        
        # Feature: Encryption (1 to 5)
        X_enc = np.random.randint(1, 6, n_samples)
        # Feature: Device Count (1 to 50)
        X_dev = np.random.randint(1, 51, n_samples)
        # Feature: Unknown Devices (0 to X_dev)
        X_unk = np.array([np.random.randint(0, dev + 1) for dev in X_dev])
        # Feature: Open Ports (0 to 10)
        X_port = np.random.randint(0, 11, n_samples)

        # Baseline Target Generation matching Rule logic but continuous
        # Weighted importance: Encryption (40%), Unk (30%), Port (20%), Dev (10%)
        # Normalizing to 0-100 scale
        
        y_enc = (X_enc - 1) / 4.0 * 100 * 0.40
        y_unk = np.clip(X_unk / 10.0, 0, 1) * 100 * 0.30
        y_port = np.clip(X_port / 5.0, 0, 1) * 100 * 0.20
        y_dev = np.clip((X_dev - 5) / 20.0, 0, 1) * 100 * 0.10
        
        y = y_enc + y_unk + y_port + y_dev
        y = np.clip(y + np.random.normal(0, 5, n_samples), 0, 100).astype(int) # add realistic noise and map to classification bins

        X = pd.DataFrame({
            "encryption": X_enc,
            "device_count": X_dev,
            "unknown_devices": X_unk,
            "open_ports": X_port
        })
        
        self.model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        self.model.fit(X, y)
        
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        print("[+] Random Forest Model trained and saved.")

    def predict_risk(self, encoded_features):
        """Expects a dictionary: {encryption: int, device_count: int, unknown_devices: int, open_ports: int}"""
        df = pd.DataFrame([encoded_features])
        score = self.model.predict(df)[0]
        return np.clip(score, 0, 100)
