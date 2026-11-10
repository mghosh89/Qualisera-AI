"""
Qualisera AI - Model Drift Monitoring
Tracks AI model performance metrics over time to detect drift.
"""
import mlflow
import pandas as pd
from datetime import datetime

class ModelMonitor:
    """Monitors healthcare AI models for drift and degradation."""
    
    def __init__(self, experiment_name: str = "qualisera_ai_monitoring"):
        mlflow.set_experiment(experiment_name)
    
    def log_prediction_metrics(self, predictions: list, actuals: list = None):
        """Log prediction statistics for drift detection."""
        with mlflow.start_run(run_name=f"monitoring_{datetime.now().strftime('%Y%m%d_%H%M')}"):
            # Calculate metrics
            avg_risk = sum(p["risk_score"] for p in predictions) / len(predictions)
            high_risk_pct = sum(1 for p in predictions if p["risk_category"] == "HIGH") / len(predictions)
            
            # Log to MLflow
            mlflow.log_metric("avg_risk_score", avg_risk)
            mlflow.log_metric("high_risk_percentage", high_risk_pct)
            mlflow.log_metric("total_predictions", len(predictions))
            mlflow.log_param("model_version", predictions[0]["model_version"])
            mlflow.log_param("timestamp", datetime.now().isoformat())
            
            print(f"📊 Logged metrics: avg_risk={avg_risk:.3f}, high_risk={high_risk_pct:.1%}")
    
    def detect_drift(self, baseline_avg: float, current_avg: float, threshold: float = 0.1) -> bool:
        """Detect if model predictions have drifted significantly."""
        drift = abs(current_avg - baseline_avg)
        is_drifted = drift > threshold
        
        if is_drifted:
            print(f"⚠️  DRIFT DETECTED: Baseline={baseline_avg:.3f}, Current={current_avg:.3f}, Δ={drift:.3f}")
        else:
            print(f"✅ No drift: Baseline={baseline_avg:.3f}, Current={current_avg:.3f}")
        
        return is_drifted

if __name__ == "__main__":
    monitor = ModelMonitor()
    
    # Simulate some predictions
    sample_predictions = [
        {"patient_id": "P1", "risk_score": 0.2, "risk_category": "LOW", "model_version": "v1.0"},
        {"patient_id": "P2", "risk_score": 0.5, "risk_category": "MODERATE", "model_version": "v1.0"},
        {"patient_id": "P3", "risk_score": 0.8, "risk_category": "HIGH", "model_version": "v1.0"},
    ]
    
    monitor.log_prediction_metrics(sample_predictions)