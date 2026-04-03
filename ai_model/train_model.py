import pandas as pd
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib
import os

class RiskModelTrainer:
    def __init__(self, data_path="data/training_dataset.csv", rf_model_path="ai_model/risk_model.joblib", if_model_path="ai_model/anomaly_model.joblib"):
        self.data_path = data_path
        self.rf_model_path = rf_model_path
        self.if_model_path = if_model_path

    def train(self):
        if not os.path.exists(self.data_path):
            print(f"[!] Data file {self.data_path} not found. Generate it first.")
            return

        df = pd.read_csv(self.data_path)
        # Features for both models
        X = df.drop(columns=['risk_score'])
        y = df['risk_score']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # 1. Train Random Forest (Supervised - Risk Prediction)
        print("[*] Training Random Forest model for risk prediction...")
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)

        predictions = rf_model.predict(X_test)
        mae = mean_absolute_error(y_test, predictions)
        print(f"[+] RF Model trained. Mean Absolute Error: {mae:.2f}")

        joblib.dump(rf_model, self.rf_model_path)
        print(f"[+] RF Model saved to {self.rf_model_path}")

        # 2. Train Isolation Forest (Unsupervised - Anomaly Detection)
        print("[*] Training Isolation Forest model for anomaly detection...")
        # We train on the whole feature set X (usually IF is unsupervised)
        if_model = IsolationForest(contamination=0.05, random_state=42)
        if_model.fit(X) # Unsupervised learning

        joblib.dump(if_model, self.if_model_path)
        print(f"[+] Isolation Forest Model saved to {self.if_model_path}")

if __name__ == "__main__":
    from ai_model.dataset_generator import generate_synthetic_dataset
    print("[*] Generating fresh dataset...")
    generate_synthetic_dataset()
    
    trainer = RiskModelTrainer()
    trainer.train()
    
    df = pd.read_csv("data/training_dataset.csv")
    print(df.head())

