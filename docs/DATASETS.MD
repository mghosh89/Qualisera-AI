# Healthcare Dataset Guide

Qualisera AI is proprietary software. It uses synthetic and publicly available
healthcare test data; the data and any third-party tools remain subject to their
own access terms, licenses, and restrictions. The project does not claim
ownership of those external materials.

## Supported sources

| Source | Data type | Project use |
|---|---|---|
| Synthea | Synthetic patient records | Patient and observation data-quality tests |
| FHIR test bundles | FHIR resources | Patient, Observation, and bundle validation |
| NIH Chest X-ray | Public image metadata and labels | Metadata schema and finding-label tests |

Use the source-specific download and setup instructions in the project
documentation. Do not assume that public availability means unrestricted use;
review the applicable terms before downloading, redistributing, or using data.

## Local test data

The test suite expects datasets under the configured data directories. Keep
downloaded datasets and generated patient data out of source control unless the
rights holder and applicable data terms explicitly permit redistribution.
Automated checks are software quality tests, not clinical validation or
diagnostic guidance.
