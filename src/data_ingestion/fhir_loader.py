"""
FHIR Test Data Loader
Loads HL7 FHIR standard test datasets
"""
import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any
import requests
from fhir.resources.condition import Condition
from fhir.resources.observation import Observation
from fhir.resources.patient import Patient


class FHIRDataLoader:
    """Loader for FHIR standard test data"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data_dir = Path(config.get("data_dir", "data/fhir")).expanduser()
        if not self.data_dir.is_absolute():
            project_root = Path(__file__).resolve().parents[2]
            self.data_dir = project_root / self.data_dir
        self.fhir_server = config.get("fhir_server", "https://hapi.fhir.org/baseR4")

    def download_test_data(self) -> Path:
        """Download FHIR test data from public servers"""
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Example: Download from HAPI FHIR test server
        try:
            response = requests.get(
                f"{self.fhir_server}/Patient?_count=100",
                headers={"Accept": "application/fhir+json"}
            )

            if response.status_code == 200:
                bundle = response.json()
                output_file = self.data_dir / "test_patients.json"
                with open(output_file, 'w') as f:
                    json.dump(bundle, f, indent=2)
                print(f"✓ Downloaded {len(bundle.get('entry', []))} patients")
                return output_file
        except Exception as e:
            print(f"Error downloading FHIR data: {e}")

        return self.data_dir

    def load_patients(self) -> pd.DataFrame:
        """Load Patient resources"""
        patients_file = self.data_dir / "test_patients.json"
        patient_bundle_files = (
            self.data_dir / "patient_bundle.json",
            self.data_dir / "patients.json",
        )
        local_files = next(
            (
                [path]
                for path in (patients_file, *patient_bundle_files)
                if path.is_file()
            ),
            sorted(self.data_dir.glob("*_bundle.json")),
        )
        if not local_files:
            self.download_test_data()
            local_files = [patients_file] if patients_file.is_file() else []

        patients_data = []
        for resource_file in local_files:
            with resource_file.open() as file:
                bundle = json.load(file)
            resources = (
                [entry.get("resource", {}) for entry in bundle.get("entry", [])]
                if bundle.get("resourceType") == "Bundle"
                else [bundle]
            )
            for patient in resources:
                if patient.get("resourceType") != "Patient":
                    continue
                names = patient.get("name") or [{}]
                patients_data.append({
                    "id": patient.get("id"),
                    "gender": patient.get("gender"),
                    "birthDate": patient.get("birthDate"),
                    "name": names[0].get("text", ""),
                })

        return pd.DataFrame(patients_data)

    def load_observations(self, patient_id: str = None) -> pd.DataFrame:
        """Load Observation resources"""
        bundle_file = self.data_dir / "observation_bundle.json"
        if bundle_file.is_file():
            with bundle_file.open() as file:
                bundle = json.load(file)
            observations = []
            for entry in bundle.get("entry", []):
                observation = entry.get("resource", {})
                if observation.get("resourceType") != "Observation":
                    continue
                observations.append({
                    "id": observation.get("id"),
                    "code": observation.get("code", {}).get("text"),
                    "value": observation.get("valueQuantity", {}).get("value"),
                    "unit": observation.get("valueQuantity", {}).get("unit"),
                    "date": observation.get("effectiveDateTime"),
                })
            return pd.DataFrame(observations)

        try:
            url = f"{self.fhir_server}/Observation"
            if patient_id:
                url += f"?subject={patient_id}"
            url += "&_count=100"

            response = requests.get(
                url,
                headers={"Accept": "application/fhir+json"}
            )

            if response.status_code == 200:
                bundle = response.json()
                obs_data = []
                for entry in bundle.get("entry", []):
                    obs = entry["resource"]
                    obs_data.append({
                        "id": obs.get("id"),
                        "code": obs.get("code", {}).get("text"),
                        "value": obs.get("valueQuantity", {}).get("value"),
                        "unit": obs.get("valueQuantity", {}).get("unit"),
                        "date": obs.get("effectiveDateTime")
                    })
                return pd.DataFrame(obs_data)
        except Exception as e:
            print(f"Error loading FHIR observations: {e}")

        return pd.DataFrame()

    def validate_fhir_resource(self, resource: Dict, resource_type: str) -> bool:
        """Validate FHIR resource against standard"""
        try:
            if not isinstance(resource, dict) or resource.get("resourceType") != resource_type:
                return False

            if resource_type == "Patient":
                if resource.get("gender") not in {None, "male", "female", "other", "unknown"}:
                    return False
                Patient.model_validate(resource)
            elif resource_type == "Observation":
                valid_statuses = {
                    "registered",
                    "preliminary",
                    "final",
                    "amended",
                    "corrected",
                    "cancelled",
                    "entered-in-error",
                    "unknown",
                }
                if resource.get("status") not in valid_statuses:
                    return False
                Observation.model_validate(resource)
            elif resource_type == "Condition":
                Condition.model_validate(resource)
            else:
                return False
            return True
        except Exception as e:
            print(f"Validation error: {e}")
            return False

    def validate_patient_bundle(self, bundle: Dict[str, Any]) -> bool:
        """Validate Patient resources and require unique, nonblank resource IDs."""
        if not isinstance(bundle, dict) or bundle.get("resourceType") != "Bundle":
            return False
        entries = bundle.get("entry")
        if not isinstance(entries, list) or not entries:
            return False

        patient_ids = []
        for entry in entries:
            if not isinstance(entry, dict):
                return False
            patient = entry.get("resource")
            if not isinstance(patient, dict) or not self.validate_fhir_resource(
                patient, "Patient"
            ):
                return False
            patient_id = patient.get("id")
            if not isinstance(patient_id, str) or not patient_id.strip():
                return False
            patient_ids.append(patient_id)

        return len(patient_ids) == len(set(patient_ids))

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of FHIR data"""
        patients = self.load_patients()

        return {
            "dataset_type": "FHIR Test Data",
            "fhir_server": self.fhir_server,
            "total_patients": len(patients),
            "data_directory": str(self.data_dir)
        }