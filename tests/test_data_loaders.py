import json

import pandas as pd
import pytest

from src.data_ingestion.fhir_loader import FHIRDataLoader
from src.data_ingestion.nih_loader import NIHDataLoader


def test_nih_loader_reads_versioned_metadata_and_local_images(tmp_path):
    data_dir = tmp_path / "nih_cxr"
    data_dir.mkdir()
    metadata = pd.DataFrame(
        {
            "Image Index": ["image1.png", "image2.png", "image3.png"],
            "Finding Labels": ["No Finding", "Atelectasis|Effusion", "Effusion"],
        }
    )
    metadata.to_csv(data_dir / "Data_Entry_2017_v2020.csv", index=False)
    (data_dir / "image1.png").touch()
    (data_dir / "image2.png").touch()

    loader = NIHDataLoader({"data_dir": str(data_dir)})
    summary = loader.get_summary()
    statistics = loader.get_disease_statistics()

    assert summary["total_images"] == 3
    assert summary["available_images"] == 2
    assert statistics.loc["count", "Effusion"] == 2
    assert statistics.loc["percentage", "Effusion"] == pytest.approx(200 / 3)


def test_fhir_loader_reads_local_bundle_without_network(tmp_path):
    data_dir = tmp_path / "fhir"
    data_dir.mkdir()
    bundle = {
        "resourceType": "Bundle",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "patient-1",
                    "gender": "female",
                    "birthDate": "2000-01-01",
                }
            },
            {"resource": {"resourceType": "Observation", "id": "observation-1"}},
        ],
    }
    (data_dir / "patients.json").write_text(json.dumps(bundle))

    patients = FHIRDataLoader({"data_dir": str(data_dir)}).load_patients()

    assert len(patients) == 1
    assert patients.iloc[0]["id"] == "patient-1"
