"""Deterministic rule-based mock inference API (§5.4).

NOT a trained or clinically validated model. A QA target only.
Note: the 400-handler uses 30-220; the (stubbed) validator screen
uses 40-180. Per §5.4 these are intentionally NOT connected here —
the orchestration gate (harness/orchestration/gate.py) is the
future-extension showcase that wires them.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class Vitals(BaseModel):
    patient_id: str
    age: int
    heart_rate: float
    systolic_bp: float
    diastolic_bp: float      # required by schema, unused in score (§5.4)
    temp_f: float


app = FastAPI(title="QualiseraAI mock predict")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(v: Vitals):
    if v.heart_rate < 30 or v.heart_rate > 220:
        raise HTTPException(status_code=400, detail="Invalid heart rate")
    score = 0
    if v.heart_rate > 100:    score += 2
    if v.systolic_bp > 140:   score += 2
    if v.age > 65:            score += 1
    if v.temp_f > 100.4:      score += 1
    level = "LOW" if score <= 1 else "MODERATE" if score <= 3 else "HIGH"
    return {"patient_id": v.patient_id, "risk": level, "score": score}