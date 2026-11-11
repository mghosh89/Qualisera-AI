# Test Scenarios

The test suite groups scenarios by dataset and expected behavior. Positive
scenarios verify valid data and successful operations; negative scenarios verify
that invalid or incomplete inputs are rejected or reported.

The dashboard at `reports/test_report.html` is generated from the latest pytest
JUnit results by running `./run_tests.sh`. It shows run totals, results per test
suite, and the 100 named dataset scenarios in separate positive and negative
lists. API scenarios are displayed separately and are not part of that count.
These are synthetic/dataset quality checks, not diagnostic or treatment rules.

## Synthea

| Type | Scenario name | Expected result |
|---|---|---|
| Positive | `test_synthea_patients_load_successfully` | Patient CSV loads with records. |
| Positive | `test_synthea_patients_have_required_columns` | Patient ID, birth date, and gender columns exist. |
| Positive | `test_synthea_gender_values_valid` | Every source gender value is supported. |
| Positive | `test_synthea_observations_load` | Observations load with descriptions. |
| Positive | `test_synthea_data_quality_passes` | Patient records pass quality checks. |
| Negative | `test_synthea_rejects_heart_rate_above_180_bpm` | Out-of-range heart rate fails validation. |
| Negative | `test_synthea_rejects_missing_patient_id` | A null patient ID fails validation. |
| Negative | `test_synthea_rejects_unsupported_gender` | Unsupported gender fails validation. |
| Negative | `test_synthea_rejects_future_birthdate` | A future birth date fails validation. |
| Negative | `test_synthea_rejects_empty_patient_dataframe` | An empty patient table fails validation. |

## FHIR

| Type | Scenario name | Expected result |
|---|---|---|
| Positive | `test_fhir_patients_load` | Local Patient resources load. |
| Positive | `test_fhir_patient_has_id` | Every loaded patient has an ID. |
| Positive | `test_fhir_patient_has_gender` | Loaded patients contain gender values. |
| Positive | `test_fhir_observations_load` | Observation resources return a DataFrame. |
| Positive | `test_fhir_resource_validation` | The saved Patient bundle is valid JSON. |
| Negative | `test_fhir_rejects_unsupported_resource_type` | Unsupported resource types are rejected. |
| Negative | `test_fhir_rejects_resource_missing_resource_type` | A missing resource type is rejected. |
| Negative | `test_fhir_rejects_unsupported_patient_gender` | An unsupported Patient gender is rejected. |
| Negative | `test_fhir_empty_patient_bundle_returns_no_patients` | An empty Patient bundle yields no patient rows. |
| Negative | `test_fhir_malformed_local_json_raises_decode_error` | Malformed JSON raises a decode error. |

## NIH Chest X-ray

| Type | Scenario name | Expected result |
|---|---|---|
| Positive | `test_nih_metadata_csv_loads_successfully` | Versioned NIH metadata loads. |
| Positive | `test_nih_metadata_contains_image_index` | Metadata includes image identifiers. |
| Positive | `test_nih_metadata_contains_finding_labels` | Metadata includes finding labels. |
| Positive | `test_nih_image_paths_are_resolved` | Metadata records resolve to image paths. |
| Positive | `test_nih_finding_statistics_are_calculated` | Finding-label statistics are calculated. |
| Positive | `test_nih_metadata_passes_schema_and_label_validation` | Valid metadata passes schema and label checks. |
| Negative | `test_nih_missing_metadata_file_is_reported` | A missing metadata file returns an empty dataset. |
| Negative | `test_nih_missing_local_image_is_reported` | A missing image is counted as unavailable. |
| Negative | `test_nih_missing_finding_label_column_fails_validation` | Missing finding labels fail schema validation. |
| Negative | `test_nih_duplicate_image_index_fails_validation` | Duplicate image identifiers fail validation. |
| Negative | `test_nih_unsupported_finding_label_fails_validation` | Unsupported finding labels fail validation. |

## Additional named dataset scenarios

The following parameterized cases bring dataset coverage to exactly 100:
Synthea 33, FHIR 34, and NIH 33. Each bracketed value is the pytest scenario ID
and appears as the scenario name in the dashboard.

### Synthea (23 additional)

| Type | Scenario name | Expected result |
|---|---|---|
| Positive | `test_synthea_valid_patient_demographics[male-patient]` | A valid male patient passes demographic validation. |
| Positive | `test_synthea_valid_patient_demographics[female-patient]` | A valid female patient passes demographic validation. |
| Positive | `test_synthea_valid_patient_demographics[other-gender]` | The supported `Other` gender passes validation. |
| Positive | `test_synthea_valid_patient_demographics[earliest-supported-birthdate]` | The supported lower birth-date boundary passes. |
| Positive | `test_synthea_valid_patient_demographics[historical-birthdate]` | A valid historical birth date passes. |
| Positive | `test_synthea_valid_patient_demographics[deathdate-after-birthdate]` | A death date after birth passes chronology checks. |
| Positive | `test_synthea_valid_patient_demographics[blank-deathdate-for-living-patient]` | A blank death date is accepted for a living patient. |
| Positive | `test_synthea_valid_heart_rate[minimum-supported-heart-rate]` | Heart rate at 40 bpm passes. |
| Positive | `test_synthea_valid_heart_rate[low-normal-heart-rate]` | Heart rate at 60 bpm passes. |
| Positive | `test_synthea_valid_heart_rate[high-normal-heart-rate]` | Heart rate at 120 bpm passes. |
| Positive | `test_synthea_valid_heart_rate[maximum-supported-heart-rate]` | Heart rate at 180 bpm passes. |
| Positive | `test_synthea_valid_heart_rate[decimal-heart-rate]` | A numeric decimal heart rate passes. |
| Negative | `test_synthea_rejects_invalid_patient_demographics[duplicate-patient-id]` | Duplicate patient IDs fail validation. |
| Negative | `test_synthea_rejects_invalid_patient_demographics[blank-patient-id]` | A whitespace-only patient ID fails validation. |
| Negative | `test_synthea_rejects_invalid_patient_demographics[malformed-birthdate]` | A malformed birth date fails validation. |
| Negative | `test_synthea_rejects_invalid_patient_demographics[birthdate-before-supported-range]` | A birth date before 1900 fails validation. |
| Negative | `test_synthea_rejects_invalid_patient_demographics[deathdate-before-birthdate]` | A death date before birth fails chronology checks. |
| Negative | `test_synthea_rejects_invalid_patient_demographics[future-deathdate]` | A future death date fails chronology checks. |
| Negative | `test_synthea_rejects_invalid_heart_rate_data[heart-rate-below-minimum]` | Heart rate below 40 bpm fails. |
| Negative | `test_synthea_rejects_invalid_heart_rate_data[non-numeric-heart-rate]` | A nonnumeric heart-rate value fails. |
| Negative | `test_synthea_rejects_invalid_heart_rate_data[null-heart-rate]` | A null heart-rate value fails. |
| Negative | `test_synthea_rejects_invalid_heart_rate_data[empty-observation-table]` | An empty observation table fails. |
| Negative | `test_synthea_rejects_invalid_heart_rate_data[missing-observation-description-column]` | Missing observation descriptions fail schema validation. |

### FHIR (23 additional)

| Type | Scenario name | Expected result |
|---|---|---|
| Positive | `test_fhir_accepts_supported_patient_gender[male]` | FHIR `male` is accepted. |
| Positive | `test_fhir_accepts_supported_patient_gender[female]` | FHIR `female` is accepted. |
| Positive | `test_fhir_accepts_supported_patient_gender[other]` | FHIR `other` is accepted. |
| Positive | `test_fhir_accepts_supported_patient_gender[unknown]` | FHIR `unknown` is accepted. |
| Positive | `test_fhir_accepts_patient_without_optional_demographics` | A Patient without optional gender or birth date passes. |
| Positive | `test_fhir_accepts_bundle_with_distinct_patient_ids` | A bundle with distinct Patient IDs passes. |
| Positive | `test_fhir_accepts_supported_observation_status[registered-observation]` | `registered` Observation status passes. |
| Positive | `test_fhir_accepts_supported_observation_status[preliminary-observation]` | `preliminary` Observation status passes. |
| Positive | `test_fhir_accepts_supported_observation_status[final-observation]` | `final` Observation status passes. |
| Positive | `test_fhir_accepts_supported_observation_status[amended-observation]` | `amended` Observation status passes. |
| Positive | `test_fhir_accepts_supported_observation_status[corrected-observation]` | `corrected` Observation status passes. |
| Negative | `test_fhir_rejects_invalid_resource_fields[malformed-patient-birthdate]` | A malformed Patient birth date is rejected. |
| Negative | `test_fhir_rejects_invalid_resource_fields[observation-missing-status]` | An Observation without required status is rejected. |
| Negative | `test_fhir_rejects_invalid_observation_status` | A non-FHIR Observation status is rejected. |
| Negative | `test_fhir_rejects_invalid_patient_bundle[missing-bundle-resource-type]` | A bundle without `resourceType` is rejected. |
| Negative | `test_fhir_rejects_invalid_patient_bundle[wrong-bundle-resource-type]` | A non-Bundle resource is rejected as a Patient bundle. |
| Negative | `test_fhir_rejects_invalid_patient_bundle[empty-patient-bundle]` | A bundle without entries is rejected. |
| Negative | `test_fhir_rejects_invalid_patient_bundle[bundle-entry-is-not-a-list]` | A non-list entry collection is rejected. |
| Negative | `test_fhir_rejects_invalid_patient_bundle[malformed-bundle-entry]` | A malformed entry is rejected. |
| Negative | `test_fhir_rejects_invalid_patient_bundle[non-patient-resource-in-patient-bundle]` | A non-Patient resource in the Patient bundle is rejected. |
| Negative | `test_fhir_rejects_invalid_patient_bundle[patient-missing-resource-id]` | A Patient without a resource ID is rejected. |
| Negative | `test_fhir_rejects_invalid_patient_bundle[blank-patient-resource-id]` | A whitespace-only resource ID is rejected. |
| Negative | `test_fhir_rejects_invalid_patient_bundle[duplicate-patient-resource-id]` | Duplicate Patient resource IDs are rejected. |

### NIH Chest X-ray (21 additional)

| Type | Scenario name | Expected result |
|---|---|---|
| Positive | `test_nih_accepts_valid_metadata_records[single-valid-finding]` | One supported finding label passes. |
| Positive | `test_nih_accepts_valid_metadata_records[multiple-findings]` | Multiple supported labels pass. |
| Positive | `test_nih_accepts_valid_metadata_records[no-finding-label]` | `No Finding` alone passes. |
| Positive | `test_nih_accepts_valid_metadata_records[multiple-images-for-one-patient]` | Distinct images for one patient are allowed. |
| Positive | `test_nih_accepts_valid_metadata_records[age-zero]` | Patient age zero passes the supported range. |
| Positive | `test_nih_accepts_valid_metadata_records[age-95]` | Patient age 95 passes the supported range. |
| Positive | `test_nih_accepts_valid_metadata_records[male-patient]` | Patient gender `M` passes. |
| Positive | `test_nih_accepts_valid_metadata_records[female-patient]` | Patient gender `F` passes. |
| Positive | `test_nih_accepts_valid_metadata_records[anterior-posterior-view]` | `AP` view position passes. |
| Positive | `test_nih_accepts_valid_metadata_records[posterior-anterior-view]` | `PA` view position passes. |
| Negative | `test_nih_rejects_invalid_metadata_records[empty-metadata]` | Metadata with no records is rejected. |
| Negative | `test_nih_rejects_invalid_metadata_records[null-image-index]` | A null image index is rejected. |
| Negative | `test_nih_rejects_invalid_metadata_records[blank-image-index]` | A blank image index is rejected. |
| Negative | `test_nih_rejects_invalid_metadata_records[image-path-traversal]` | An image index containing a path is rejected. |
| Negative | `test_nih_rejects_invalid_metadata_records[null-finding-label]` | A null finding label is rejected. |
| Negative | `test_nih_rejects_invalid_metadata_records[blank-finding-label]` | A blank finding label is rejected. |
| Negative | `test_nih_rejects_invalid_metadata_records[contradictory-no-finding-label]` | `No Finding` combined with another label is rejected. |
| Negative | `test_nih_rejects_invalid_metadata_records[negative-patient-age]` | A negative patient age is rejected. |
| Negative | `test_nih_rejects_invalid_metadata_records[patient-age-over-120]` | Patient age above 120 is rejected. |
| Negative | `test_nih_rejects_invalid_metadata_records[unsupported-patient-gender]` | An unsupported patient gender is rejected. |
| Negative | `test_nih_rejects_invalid_metadata_records[unsupported-view-position]` | An unsupported view position is rejected. |

The two dataset-loader regression scenarios included in the 100 are
`test_nih_loader_reads_versioned_metadata_and_local_images` and
`test_fhir_loader_reads_local_bundle_without_network`.

## API

API tests cover health checks, valid low- and high-risk predictions, invalid
heart-rate rejection, required fields, response time, and repeated requests.
Their individual outcomes appear under API suites in the dashboard.

## Run and refresh the dashboard

```bash
./run_tests.sh
```

The script runs the complete test suite, writes a temporary JUnit result file,
and refreshes `reports/test_report.html`. It preserves pytest's exit code so a
failed test run still exits unsuccessfully after the dashboard is written.
