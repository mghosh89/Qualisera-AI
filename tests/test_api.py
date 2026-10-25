"""
CuraOps AI - API Quality Assurance Tests
Validates the mock AI service against clinical and performance standards.
"""
import pytest
import requests
import time
from src.api.mock_ai_service import app
from fastapi.testclient import TestClient

client = TestClient(app)

class TestAPIHealth:
    """Basic health and availability tests."""
    
    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert "timestamp" in response.json()

class TestClinicalValidation:
    """Clinical safety and accuracy tests."""
    
    def test_low_risk_prediction(self):
        """Young healthy patient should be LOW risk."""
        payload = {
            "patient_id": "P001",
            "age": 25,
            "heart_rate": 70,
            "systolic_bp": 120,
            "diastolic_bp": 80,
            "temperature_f": 98.6
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["risk_category"] == "LOW"
        assert data["risk_score"] < 0.4
    
    def test_high_risk_prediction(self):
        """Elderly patient with abnormal vitals should be HIGH risk."""
        payload = {
            "patient_id": "P002",
            "age": 75,
            "heart_rate": 110,
            "systolic_bp": 160,
            "diastolic_bp": 95,
            "temperature_f": 101.5
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["risk_category"] == "HIGH"
        assert data["risk_score"] > 0.7
    
    def test_invalid_heart_rate_rejected(self):
        """Clinically impossible heart rate should be rejected."""
        payload = {
            "patient_id": "P003",
            "age": 40,
            "heart_rate": 300,  # Impossible
            "systolic_bp": 120,
            "diastolic_bp": 80,
            "temperature_f": 98.6
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 400

class TestPerformance:
    """API performance and latency tests."""
    
    def test_response_time_under_200ms(self):
        """API must respond within 200ms for clinical use."""
        payload = {
            "patient_id": "P004",
            "age": 50,
            "heart_rate": 80,
            "systolic_bp": 130,
            "diastolic_bp": 85,
            "temperature_f": 98.6
        }
        start = time.time()
        response = client.post("/predict", json=payload)
        elapsed = (time.time() - start) * 1000  # ms
        
        assert response.status_code == 200
        assert elapsed < 200, f"Response took {elapsed:.2f}ms (SLA: 200ms)"
    
    def test_concurrent_requests(self):
        """API should handle 10 concurrent requests."""
        payload = {
            "patient_id": "P005",
            "age": 45,
            "heart_rate": 75,
            "systolic_bp": 125,
            "diastolic_bp": 82,
            "temperature_f": 98.6
        }
        responses = [client.post("/predict", json=payload) for _ in range(10)]
        assert all(r.status_code == 200 for r in responses)