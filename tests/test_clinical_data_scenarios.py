import pandas as pd
import pytest

from src.data_ingestion.fhir_loader import FHIRDataLoader
from src.data_ingestion.nih_loader import NIHDataLoader
from src.data_quality.validate_healthcare_data import HealthcareDataValidator


@pytest.fixture
def synthea_validator(tmp_path):
    return HealthcareDataValidator(data_dir=tmp_path)


@pytest.fixture
def fhir_loader(tmp_path):
    return FHIRDataLoader({"data_dir": str(tmp_path)})


@pytest.fixture
def nih_loader(tmp_path):
    return NIHDataLoader({"data_dir": str(tmp_path)})


def _patient(patient_id="patient-1", birthdate="2000-01-01", gender="M", **extra):
    return {
        "Id": patient_id,
        "BIRTHDATE": birthdate,
        "GENDER": gender,
        **extra,
    }


class TestSyntheaPositive:
    @pytest.mark.parametrize(
        ("gender", "birthdate", "deathdate"),
        [
            pytest.param("M", "2000-01-01", None, id="male-patient"),
            pytest.param("F", "2000-01-01", None, id="female-patient"),
            pytest.param("Other", "2000-01-01", None, id="other-gender"),
            pytest.param("M", "1900-01-01", None, id="earliest-supported-birthdate"),
            pytest.param("F", "2024-06-15", None, id="historical-birthdate"),
            pytest.param(
                "M", "1980-03-04", "2020-03-04", id="deathdate-after-birthdate"
            ),
            pytest.param("F", "1980-03-04", "", id="blank-deathdate-for-living-patient"),
        ],
    )
    def test_synthea_valid_patient_demographics(
        self, synthea_validator, gender, birthdate, deathdate
    ):
        patients = pd.DataFrame(
            [_patient(gender=gender, birthdate=birthdate, DEATHDATE=deathdate)]
        )
        assert synthea_validator.validate_patient_dataframe(patients)["success"]

    @pytest.mark.parametrize(
        "heart_rate",
        [
            pytest.param("40", id="minimum-supported-heart-rate"),
            pytest.param("60", id="low-normal-heart-rate"),
            pytest.param("120", id="high-normal-heart-rate"),
            pytest.param("180", id="maximum-supported-heart-rate"),
            pytest.param("72.5", id="decimal-heart-rate"),
        ],
    )
    def test_synthea_valid_heart_rate(
        self, synthea_validator, heart_rate
    ):
        observations = pd.DataFrame(
            {"DESCRIPTION": ["Heart rate"], "VALUE": [heart_rate]}
        )
        assert synthea_validator.validate_vitals_dataframe(observations)["success"]


class TestSyntheaNegative:
    @pytest.mark.parametrize(
        "patients",
        [
            pytest.param(
                pd.DataFrame(
                    [_patient("duplicate"), _patient("duplicate", gender="F")]
                ),
                id="duplicate-patient-id",
            ),
            pytest.param(
                pd.DataFrame([_patient("   ")]), id="blank-patient-id"
            ),
            pytest.param(
                pd.DataFrame([_patient(birthdate="not-a-date")]),
                id="malformed-birthdate",
            ),
            pytest.param(
                pd.DataFrame([_patient(birthdate="1899-12-31")]),
                id="birthdate-before-supported-range",
            ),
            pytest.param(
                pd.DataFrame(
                    [_patient(birthdate="2000-01-02", DEATHDATE="2000-01-01")]
                ),
                id="deathdate-before-birthdate",
            ),
            pytest.param(
                pd.DataFrame([_patient(DEATHDATE="2999-01-01")]),
                id="future-deathdate",
            ),
        ],
    )
    def test_synthea_rejects_invalid_patient_demographics(
        self, synthea_validator, patients
    ):
        assert not synthea_validator.validate_patient_dataframe(patients)["success"]

    @pytest.mark.parametrize(
        "observations",
        [
            pytest.param(
                pd.DataFrame({"DESCRIPTION": ["Heart rate"], "VALUE": [39]}),
                id="heart-rate-below-minimum",
            ),
            pytest.param(
                pd.DataFrame({"DESCRIPTION": ["Heart rate"], "VALUE": ["unknown"]}),
                id="non-numeric-heart-rate",
            ),
            pytest.param(
                pd.DataFrame({"DESCRIPTION": ["Heart rate"], "VALUE": [None]}),
                id="null-heart-rate",
            ),
            pytest.param(
                pd.DataFrame(columns=["DESCRIPTION", "VALUE"]),
                id="empty-observation-table",
            ),
            pytest.param(
                pd.DataFrame({"VALUE": [72]}),
                id="missing-observation-description-column",
            ),
        ],
    )
    def test_synthea_rejects_invalid_heart_rate_data(
        self, synthea_validator, observations
    ):
        assert not synthea_validator.validate_vitals_dataframe(observations)["success"]


class TestFHIRPositive:
    @pytest.mark.parametrize(
        "gender",
        [
            pytest.param("male", id="male"),
            pytest.param("female", id="female"),
            pytest.param("other", id="other"),
            pytest.param("unknown", id="unknown"),
        ],
    )
    def test_fhir_accepts_supported_patient_gender(self, fhir_loader, gender):
        patient = {
            "resourceType": "Patient",
            "id": f"patient-{gender}",
            "gender": gender,
            "birthDate": "2000-01-01",
        }
        assert fhir_loader.validate_fhir_resource(patient, "Patient")

    def test_fhir_accepts_patient_without_optional_demographics(self, fhir_loader):
        assert fhir_loader.validate_fhir_resource(
            {"resourceType": "Patient", "id": "patient-optional"}, "Patient"
        )

    def test_fhir_accepts_bundle_with_distinct_patient_ids(self, fhir_loader):
        bundle = {
            "resourceType": "Bundle",
            "entry": [
                {"resource": {"resourceType": "Patient", "id": "patient-1"}},
                {"resource": {"resourceType": "Patient", "id": "patient-2"}},
            ],
        }
        assert fhir_loader.validate_patient_bundle(bundle)

    @pytest.mark.parametrize(
        "status",
        [
            pytest.param("registered", id="registered-observation"),
            pytest.param("preliminary", id="preliminary-observation"),
            pytest.param("final", id="final-observation"),
            pytest.param("amended", id="amended-observation"),
            pytest.param("corrected", id="corrected-observation"),
        ],
    )
    def test_fhir_accepts_supported_observation_status(
        self, fhir_loader, status
    ):
        observation = {
            "resourceType": "Observation",
            "status": status,
            "code": {"text": "Heart rate"},
        }
        assert fhir_loader.validate_fhir_resource(observation, "Observation")


class TestFHIRNegative:
    @pytest.mark.parametrize(
        "resource",
        [
            pytest.param(
                {
                    "resourceType": "Patient",
                    "id": "patient-1",
                    "birthDate": "not-a-date",
                },
                id="malformed-patient-birthdate",
            ),
            pytest.param(
                {"resourceType": "Observation", "code": {"text": "Heart rate"}},
                id="observation-missing-status",
            ),
        ],
    )
    def test_fhir_rejects_invalid_resource_fields(self, fhir_loader, resource):
        resource_type = resource["resourceType"]
        assert not fhir_loader.validate_fhir_resource(resource, resource_type)

    def test_fhir_rejects_invalid_observation_status(self, fhir_loader):
        observation = {
            "resourceType": "Observation",
            "status": "invalid",
            "code": {"text": "Heart rate"},
        }
        assert not fhir_loader.validate_fhir_resource(observation, "Observation")

    @pytest.mark.parametrize(
        "bundle",
        [
            pytest.param({}, id="missing-bundle-resource-type"),
            pytest.param({"resourceType": "Patient"}, id="wrong-bundle-resource-type"),
            pytest.param(
                {"resourceType": "Bundle", "entry": []}, id="empty-patient-bundle"
            ),
            pytest.param(
                {"resourceType": "Bundle", "entry": {}},
                id="bundle-entry-is-not-a-list",
            ),
            pytest.param(
                {"resourceType": "Bundle", "entry": [None]},
                id="malformed-bundle-entry",
            ),
            pytest.param(
                {
                    "resourceType": "Bundle",
                    "entry": [{"resource": {"resourceType": "Observation", "id": "o1"}}],
                },
                id="non-patient-resource-in-patient-bundle",
            ),
            pytest.param(
                {
                    "resourceType": "Bundle",
                    "entry": [{"resource": {"resourceType": "Patient"}}],
                },
                id="patient-missing-resource-id",
            ),
            pytest.param(
                {
                    "resourceType": "Bundle",
                    "entry": [
                        {"resource": {"resourceType": "Patient", "id": "   "}}
                    ],
                },
                id="blank-patient-resource-id",
            ),
            pytest.param(
                {
                    "resourceType": "Bundle",
                    "entry": [
                        {"resource": {"resourceType": "Patient", "id": "duplicate"}},
                        {"resource": {"resourceType": "Patient", "id": "duplicate"}},
                    ],
                },
                id="duplicate-patient-resource-id",
            ),
        ],
    )
    def test_fhir_rejects_invalid_patient_bundle(self, fhir_loader, bundle):
        assert not fhir_loader.validate_patient_bundle(bundle)


def _nih_metadata(**overrides):
    record = {
        "Image Index": "image-001.png",
        "Finding Labels": "Effusion",
        **overrides,
    }
    return pd.DataFrame([record])


class TestNIHPositive:
    @pytest.mark.parametrize(
        "metadata",
        [
            pytest.param(_nih_metadata(), id="single-valid-finding"),
            pytest.param(
                _nih_metadata(**{"Finding Labels": "Atelectasis|Effusion"}),
                id="multiple-findings",
            ),
            pytest.param(
                _nih_metadata(**{"Finding Labels": "No Finding"}),
                id="no-finding-label",
            ),
            pytest.param(
                pd.DataFrame(
                    [
                        {
                            "Image Index": "image-001.png",
                            "Finding Labels": "Effusion",
                            "Patient ID": "patient-1",
                        },
                        {
                            "Image Index": "image-002.png",
                            "Finding Labels": "Pneumonia",
                            "Patient ID": "patient-1",
                        },
                    ]
                ),
                id="multiple-images-for-one-patient",
            ),
            pytest.param(
                _nih_metadata(**{"Patient Age": 0}), id="age-zero"
            ),
            pytest.param(
                _nih_metadata(**{"Patient Age": 95}), id="age-95"
            ),
            pytest.param(
                _nih_metadata(**{"Patient Gender": "M"}), id="male-patient"
            ),
            pytest.param(
                _nih_metadata(**{"Patient Gender": "F"}), id="female-patient"
            ),
            pytest.param(
                _nih_metadata(**{"View Position": "AP"}), id="anterior-posterior-view"
            ),
            pytest.param(
                _nih_metadata(**{"View Position": "PA"}), id="posterior-anterior-view"
            ),
        ],
    )
    def test_nih_accepts_valid_metadata_records(self, nih_loader, metadata):
        assert nih_loader.validate_metadata(metadata)["success"]


class TestNIHNegative:
    @pytest.mark.parametrize(
        "metadata",
        [
            pytest.param(
                pd.DataFrame(columns=["Image Index", "Finding Labels"]),
                id="empty-metadata",
            ),
            pytest.param(
                _nih_metadata(**{"Image Index": None}), id="null-image-index"
            ),
            pytest.param(
                _nih_metadata(**{"Image Index": "  "}), id="blank-image-index"
            ),
            pytest.param(
                _nih_metadata(**{"Image Index": "../outside.png"}),
                id="image-path-traversal",
            ),
            pytest.param(
                _nih_metadata(**{"Finding Labels": None}), id="null-finding-label"
            ),
            pytest.param(
                _nih_metadata(**{"Finding Labels": "  "}), id="blank-finding-label"
            ),
            pytest.param(
                _nih_metadata(**{"Finding Labels": "No Finding|Effusion"}),
                id="contradictory-no-finding-label",
            ),
            pytest.param(
                _nih_metadata(**{"Patient Age": -1}), id="negative-patient-age"
            ),
            pytest.param(
                _nih_metadata(**{"Patient Age": 121}), id="patient-age-over-120"
            ),
            pytest.param(
                _nih_metadata(**{"Patient Gender": "X"}),
                id="unsupported-patient-gender",
            ),
            pytest.param(
                _nih_metadata(**{"View Position": "LAT"}),
                id="unsupported-view-position",
            ),
        ],
    )
    def test_nih_rejects_invalid_metadata_records(self, nih_loader, metadata):
        assert not nih_loader.validate_metadata(metadata)["success"]
        if (
            not metadata.empty
            and metadata.iloc[0]["Image Index"] == "../outside.png"
        ):
            windows_path = _nih_metadata(**{"Image Index": r"..\outside.png"})
            assert not nih_loader.validate_metadata(windows_path)["success"]
