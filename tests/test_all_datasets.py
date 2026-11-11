"""
Qualisera AI - Comprehensive Test Suite
Tests all healthcare datasets with positive and negative scenarios
"""
import json

import pytest
import pandas as pd
from pathlib import Path
from src.data_ingestion import DataFactory
from src.data_quality.validate_healthcare_data import HealthcareDataValidator


# ==========================================
# TEST FIXTURES
# ==========================================

@pytest.fixture
def synthea_loader():
    """Load Synthea dataset"""
    config = {"data_dir": "data/synthea", "patient_count": 100}
    return DataFactory.get_loader("synthea", config)

@pytest.fixture
def fhir_loader():
    """Load FHIR dataset"""
    config = {"data_dir": "data/fhir", "fhir_server": "https://hapi.fhir.org/baseR4"}
    return DataFactory.get_loader("fhir", config)

@pytest.fixture
def nih_loader():
    """Load NIH Chest X-ray dataset"""
    config = {"data_dir": "data/nih_cxr"}
    return DataFactory.get_loader("nih", config)

@pytest.fixture
def validator(synthea_loader):
    """Create data quality validator"""
    return HealthcareDataValidator(data_dir=synthea_loader.data_dir)


# ==========================================
# SYNTHEA DATASET TESTS (5 Positive + 5 Negative)
# ==========================================

class TestSyntheaPositive:
    """Positive test cases for Synthea data"""

    def test_synthea_patients_load_successfully(self, synthea_loader):
        """TEST: Patients CSV loads without errors"""
        patients = synthea_loader.load_patients()
        assert not patients.empty, "Patients dataframe should not be empty"
        assert len(patients) > 0, "Should have at least 1 patient"

    def test_synthea_patients_have_required_columns(self, synthea_loader):
        """TEST: Patients have all required columns"""
        patients = synthea_loader.load_patients()
        required_cols = ["Id", "BIRTHDATE", "GENDER"]
        for col in required_cols:
            assert col in patients.columns, f"Missing required column: {col}"

    def test_synthea_gender_values_valid(self, synthea_loader):
        """TEST: Gender values are M or F only"""
        patients = synthea_loader.load_patients()
        unique_genders = patients["GENDER"].unique()
        for gender in unique_genders:
            assert gender in ["M", "F"], f"Invalid gender value: {gender}"

    def test_synthea_observations_load(self, synthea_loader):
        """TEST: Observations (vitals) data loads"""
        observations = synthea_loader.load_observations()
        assert not observations.empty, "Observations should not be empty"
        assert "DESCRIPTION" in observations.columns, "Should have DESCRIPTION column"

    def test_synthea_data_quality_passes(self, synthea_loader, validator):
        """TEST: Data passes quality validation"""
        patients = synthea_loader.load_patients()
        results = validator.validate_patient_dataframe(patients)
        assert results["success"], f"Validation should pass: {results['failed_expectations']}"


class TestSyntheaNegative:
    """Negative test cases for Synthea data"""

    def test_synthea_rejects_heart_rate_above_180_bpm(self, validator):
        """Heart rate above the supported clinical range is rejected."""
        observations = pd.DataFrame({
            "DESCRIPTION": ["Heart rate"],
            "VALUE": ["250"],
        })

        result = validator.validate_vitals_dataframe(observations)

        assert not result["success"]
        assert result["statistics"]["values_out_of_range"] == 1

    def test_synthea_rejects_missing_patient_id(self, validator):
        """Patient records with a null identifier fail quality validation."""
        patients = pd.DataFrame({
            "Id": [None],
            "BIRTHDATE": ["2000-01-01"],
            "GENDER": ["M"],
        })

        result = validator.validate_patient_dataframe(patients)

        assert not result["success"]

    def test_synthea_rejects_unsupported_gender(self, validator):
        """Patient records with an unsupported gender fail validation."""
        patients = pd.DataFrame({
            "Id": ["patient-1"],
            "BIRTHDATE": ["2000-01-01"],
            "GENDER": ["X"],
        })

        result = validator.validate_patient_dataframe(patients)

        assert not result["success"]

    def test_synthea_rejects_future_birthdate(self, validator):
        """Patient records with future birth dates fail validation."""
        from datetime import date, timedelta

        future_date = (date.today() + timedelta(days=1)).isoformat()
        patients = pd.DataFrame({
            "Id": ["patient-1"],
            "BIRTHDATE": [future_date],
            "GENDER": ["M"],
        })

        result = validator.validate_patient_dataframe(patients)

        assert not result["success"]

    def test_synthea_rejects_empty_patient_dataframe(self, validator):
        """An empty patient dataset fails quality validation."""
        result = validator.validate_patient_dataframe(pd.DataFrame())

        assert not result["success"]


# ==========================================
# FHIR DATASET TESTS (5 Positive + 5 Negative)
# ==========================================

class TestFHIRPositive:
    """Positive test cases for FHIR data"""

    def test_fhir_patients_load(self, fhir_loader):
        """TEST: FHIR Patient resources load successfully"""
        patients = fhir_loader.load_patients()
        assert not patients.empty, "FHIR patients should not be empty"

    def test_fhir_patient_has_id(self, fhir_loader):
        """TEST: Each FHIR patient has an ID"""
        patients = fhir_loader.load_patients()
        assert "id" in patients.columns, "Patients should have 'id' column"
        assert patients["id"].notnull().all(), "All patients should have IDs"

    def test_fhir_patient_has_gender(self, fhir_loader):
        """FHIR patient gender values follow the FHIR administrative-gender set."""
        patients = fhir_loader.load_patients()
        assert "gender" in patients.columns
        genders = patients["gender"].dropna()
        assert not genders.empty
        assert set(genders).issubset({"male", "female", "other", "unknown"})

    def test_fhir_observations_load(self, tmp_path):
        """FHIR Observation bundle values load from local data without networking."""
        observation = {
            "resourceType": "Observation",
            "id": "observation-1",
            "status": "final",
            "code": {"text": "Heart rate"},
            "valueQuantity": {"value": 72, "unit": "/min"},
        }
        (tmp_path / "observation_bundle.json").write_text(json.dumps({
            "resourceType": "Bundle",
            "entry": [{"resource": observation}],
        }))

        observations = DataFactory.get_loader(
            "fhir", {"data_dir": str(tmp_path)}
        ).load_observations()

        assert observations.to_dict("records") == [
            {
                "id": "observation-1",
                "code": "Heart rate",
                "value": 72,
                "unit": "/min",
                "date": None,
            }
        ]

    def test_fhir_resource_validation(self, fhir_loader):
        """The local FHIR Patient bundle contains valid, uniquely identified patients."""
        fhir_file = Path(fhir_loader.data_dir) / "patient_bundle.json"
        with fhir_file.open() as file:
            data = json.load(file)
        assert fhir_loader.validate_patient_bundle(data)


class TestFHIRNegative:
    """Negative test cases for FHIR data"""

    def test_fhir_rejects_unsupported_resource_type(self, fhir_loader):
        """FHIR resources with an unsupported type are rejected."""
        assert not fhir_loader.validate_fhir_resource(
            {"resourceType": "InvalidType"}, "InvalidType"
        )

    def test_fhir_rejects_resource_missing_resource_type(self, fhir_loader):
        """FHIR resources without resourceType are rejected."""
        assert not fhir_loader.validate_fhir_resource(
            {"gender": "female"}, "Patient"
        )

    def test_fhir_rejects_unsupported_patient_gender(self, fhir_loader):
        """FHIR Patient resources with an unsupported gender are rejected."""
        assert not fhir_loader.validate_fhir_resource(
            {"resourceType": "Patient", "gender": "invalid"}, "Patient"
        )

    def test_fhir_empty_patient_bundle_returns_no_patients(self, tmp_path):
        """An empty local Patient bundle returns an empty patient table."""
        fhir_dir = tmp_path / "fhir"
        fhir_dir.mkdir()
        (fhir_dir / "test_patients.json").write_text(
            '{"resourceType": "Bundle", "entry": []}'
        )

        patients = DataFactory.get_loader(
            "fhir", {"data_dir": str(fhir_dir)}
        ).load_patients()

        assert patients.empty

    def test_fhir_malformed_local_json_raises_decode_error(self, tmp_path):
        """Malformed FHIR JSON is surfaced as a decode error."""
        fhir_dir = tmp_path / "fhir"
        fhir_dir.mkdir()
        (fhir_dir / "test_patients.json").write_text(
            '{"resourceType": "Patient", "id": }'
        )

        with pytest.raises(ValueError):
            DataFactory.get_loader(
                "fhir", {"data_dir": str(fhir_dir)}
            ).load_patients()


# ==========================================
# NIH CHEST X-RAY TESTS (5 Positive + 5 Negative)
# ==========================================

class TestNIHPositive:
    """Positive test cases for NIH Chest X-ray data"""

    def test_nih_metadata_csv_loads_successfully(self, nih_loader):
        """NIH metadata CSV loads successfully."""
        metadata = nih_loader.download_metadata()
        assert not metadata.empty, "Metadata should not be empty"

    def test_nih_metadata_contains_image_index(self, nih_loader):
        """NIH metadata contains the image identifier column."""
        metadata = nih_loader.download_metadata()
        assert "Image Index" in metadata.columns, "Should have Image Index column"

    def test_nih_metadata_contains_finding_labels(self, nih_loader):
        """NIH metadata contains finding labels."""
        metadata = nih_loader.download_metadata()
        assert "Finding Labels" in metadata.columns
        assert metadata["Finding Labels"].notna().all()

    def test_nih_image_paths_are_resolved(self, tmp_path):
        """Metadata image references resolve to the matching local image files."""
        image = tmp_path / "image-001.png"
        image.touch()
        pd.DataFrame({
            "Image Index": ["image-001.png"],
            "Finding Labels": ["No Finding"],
        }).to_csv(tmp_path / "Data_Entry_2017.csv", index=False)
        loader = DataFactory.get_loader("nih", {"data_dir": str(tmp_path)})

        metadata = loader.load_image_paths()

        assert Path(metadata.iloc[0]["full_path"]) == image
        assert Path(metadata.iloc[0]["full_path"]).is_file()

    def test_nih_finding_statistics_are_calculated(self, nih_loader):
        """Finding-label statistics are calculated."""
        stats = nih_loader.get_disease_statistics()
        assert isinstance(stats, pd.DataFrame), "Should return DataFrame"
        assert not stats.empty

    def test_nih_metadata_passes_schema_and_label_validation(self, nih_loader):
        """Valid NIH metadata passes schema and label validation."""
        metadata = nih_loader.download_metadata()

        assert nih_loader.validate_metadata(metadata)["success"]


class TestNIHNegative:
    """Negative test cases for NIH Chest X-ray data"""

    def test_nih_missing_metadata_file_is_reported(self, tmp_path):
        """Missing NIH metadata is reported as an empty dataset."""
        loader = DataFactory.get_loader(
            "nih", {"data_dir": str(tmp_path / "empty")}
        )

        assert loader.download_metadata().empty

    def test_nih_missing_local_image_is_reported(self, tmp_path):
        """An image reference without a local file resolves as unavailable."""
        data_dir = tmp_path / "nih"
        data_dir.mkdir()
        pd.DataFrame({
            "Image Index": ["missing.png"],
            "Finding Labels": ["No Finding"],
        }).to_csv(data_dir / "Data_Entry_2017.csv", index=False)
        loader = DataFactory.get_loader("nih", {"data_dir": str(data_dir)})

        assert loader.get_summary()["available_images"] == 0

    def test_nih_missing_finding_label_column_fails_validation(self, nih_loader):
        """NIH metadata without Finding Labels fails schema validation."""
        result = nih_loader.validate_metadata(
            pd.DataFrame({"Image Index": ["001.png"]})
        )

        assert not result["success"]

    def test_nih_duplicate_image_index_fails_validation(self, nih_loader):
        """Duplicate NIH image identifiers fail metadata validation."""
        result = nih_loader.validate_metadata(pd.DataFrame({
            "Image Index": ["001.png", "001.png"],
            "Finding Labels": ["No Finding", "Effusion"],
        }))

        assert not result["success"]

    def test_nih_unsupported_finding_label_fails_validation(self, nih_loader):
        """Unsupported NIH finding labels fail metadata validation."""
        result = nih_loader.validate_metadata(pd.DataFrame({
            "Image Index": ["001.png"],
            "Finding Labels": ["Unknown Finding"],
        }))

        assert not result["success"]


# ==========================================
# API INTEGRATION TESTS (Bonus - Shows End-to-End QA)
# ==========================================

class TestAPIIntegration:
    """Integration tests showing end-to-end QA pipeline"""

    def test_api_health_check(self):
        """TEST: API health endpoint responds"""
        import requests
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            assert response.status_code == 200, "Health check should return 200"
        except requests.exceptions.ConnectionError:
            pytest.skip("API not running - start with: uvicorn src.api.mock_ai_service:app --reload")

    def test_api_prediction_endpoint(self):
        """TEST: AI prediction endpoint works"""
        import requests
        try:
            payload = {
                "patient_id": "P001",
                "age": 45,
                "heart_rate": 75,
                "systolic_bp": 120,
                "diastolic_bp": 80,
                "temperature_f": 98.6
            }
            response = requests.post("http://localhost:8000/predict", json=payload, timeout=5)
            assert response.status_code == 200, "Prediction should succeed"
            data = response.json()
            assert "risk_score" in data, "Should return risk_score"
        except requests.exceptions.ConnectionError:
            pytest.skip("API not running")

    def test_api_invalid_heart_rate_rejected(self):
        """TEST: API rejects clinically impossible values"""
        import requests
        try:
            payload = {
                "patient_id": "P002",
                "age": 45,
                "heart_rate": 300,  # Impossible
                "systolic_bp": 120,
                "diastolic_bp": 80,
                "temperature_f": 98.6
            }
            response = requests.post("http://localhost:8000/predict", json=payload, timeout=5)
            assert response.status_code == 400, "Should reject invalid heart rate"
        except requests.exceptions.ConnectionError:
            pytest.skip("API not running")

    def test_api_response_time_under_200ms(self):
        """TEST: API responds within acceptable latency"""
        import requests
        import time
        try:
            payload = {
                "patient_id": "P003",
                "age": 50,
                "heart_rate": 80,
                "systolic_bp": 125,
                "diastolic_bp": 82,
                "temperature_f": 98.6
            }
            start = time.time()
            response = requests.post("http://localhost:8000/predict", json=payload, timeout=5)
            elapsed = (time.time() - start) * 1000
            assert response.status_code == 200
            assert elapsed < 200, f"Response took {elapsed:.2f}ms (SLA: 200ms)"
        except requests.exceptions.ConnectionError:
            pytest.skip("API not running")

    def test_api_missing_required_field(self):
        """TEST: API rejects incomplete payload"""
        import requests
        try:
            payload = {
                "patient_id": "P004"
                # Missing all other required fields
            }
            response = requests.post("http://localhost:8000/predict", json=payload, timeout=5)
            assert response.status_code == 422, "Should reject incomplete payload"
        except requests.exceptions.ConnectionError:
            pytest.skip("API not running")