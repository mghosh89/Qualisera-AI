"""
Qualisera AI - Mock Healthcare AI Inference API
Simulates a clinical AI model for testing QA pipelines.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
from datetime import datetime

app = FastAPI(
    title="Qualisera AI - Mock Clinical Inference API",
    description="A test endpoint for healthcare AI QA validation",
    version="1.0.0"
)

class PatientVitals(BaseModel):
    patient_id: str
    age: int
    heart_rate: int
    systolic_bp: int
    diastolic_bp: int
    temperature_f: float

class AIPrediction(BaseModel):
    patient_id: str
    risk_score: float
    risk_category: str
    prediction_timestamp: str
    model_version: str

@app.get("/")
def root():
    return {
        "service": "Qualisera AI Mock Inference",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/predict", response_model=AIPrediction)
def predict_risk(vitals: PatientVitals):
    """
    Mock AI prediction endpoint.
    Simulates a cardiac risk assessment model.
    """
    # Validate input ranges (clinical safety)
    if vitals.heart_rate < 30 or vitals.heart_rate > 220:
        raise HTTPException(status_code=400, detail="Invalid heart rate")
    
    # Simple rule-based "AI" prediction
    risk_score = 0.0
    if vitals.heart_rate > 100:
        risk_score += 0.3
    if vitals.systolic_bp > 140:
        risk_score += 0.3
    if vitals.age > 65:
        risk_score += 0.2
    if vitals.temperature_f > 100.4:
        risk_score += 0.2
    
    risk_score = min(risk_score, 1.0)
    
    if risk_score > 0.7:
        category = "HIGH"
    elif risk_score > 0.4:
        category = "MODERATE"
    else:
        category = "LOW"
    
    return AIPrediction(
        patient_id=vitals.patient_id,
        risk_score=round(risk_score, 3),
        risk_category=category,
        prediction_timestamp=datetime.utcnow().isoformat(),
        model_version="qualisera-mock-v1.0"
    )