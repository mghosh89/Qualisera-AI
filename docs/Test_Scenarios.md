# Qualisera AI - Test Scenarios Documentation

This document outlines all test scenarios demonstrating the QA framework's capabilities.

## Test Coverage Summary

| Dataset | Positive Tests | Negative Tests | Total |
|---------|---------------|----------------|-------|
| **Synthea** | 5 | 5 | 10 |
| **FHIR** | 5 | 5 | 10 |
| **NIH Chest X-ray** | 5 | 5 | 10 |
| **API Integration** | 5 | 0 | 5 |
| **TOTAL** | **20** | **15** | **35** |

---

## 🟢 Positive Test Scenarios (Should Pass)

### Synthea Dataset

| # | Test Name | What We Test | Expected Result |
|---|-----------|--------------|-----------------|
| 1 | `test_synthea_patients_load_successfully` | Patients CSV loads without errors | ✅ Dataframe not empty |
| 2 | `test_synthea_patients_have_required_columns` | Required columns exist (Id, BIRTHDATE, GENDER) | ✅ All columns present |
| 3 | `test_synthea_gender_values_valid` | Gender values are M or F only | ✅ Only valid values |
| 4 | `test_synthea_observations_load` | Observations (vitals) data loads | ✅ Dataframe with DESCRIPTION column |
| 5 | `test_synthea_data_quality_passes` | Data passes Great Expectations validation | ✅ Validation success = True |

### FHIR Dataset

| # | Test Name | What We Test | Expected Result |
|---|-----------|--------------|-----------------|
| 1 | `test_fhir_patients_load` | FHIR Patient resources load | ✅ Dataframe not empty |
| 2 | `test_fhir_patient_has_id` | Each patient has an ID | ✅ All IDs present |
| 3 | `test_fhir_patient_has_gender` | Patients have gender field | ✅ At least one gender value |
| 4 | `test_fhir_observations_load` | Observation resources load | ✅ Returns DataFrame |
| 5 | `test_fhir_resource_validation` | Resources are valid JSON | ✅ Has resourceType = "Bundle" |

### NIH Chest X-ray Dataset

| # | Test Name | What We Test | Expected Result |
|---|-----------|--------------|-----------------|
| 1 | `test_nih_metadata_loads` | Metadata CSV loads | ✅ Dataframe not empty |
| 2 | `test_nih_metadata_has_image_index` | Has Image Index column | ✅ Column exists |
| 3 | `test_nih_metadata_has_finding_labels` | Has disease finding columns | ✅ Finding columns present |
| 4 | `test_nih_image_paths_generated` | Image paths correctly generated | ✅ Paths generated |
| 5 | `test_nih_disease_statistics` | Disease statistics calculated | ✅ Returns DataFrame |

### API Integration

| # | Test Name | What We Test | Expected Result |
|---|-----------|--------------|-----------------|
| 1 | `test_api_health_check` | API health endpoint | ✅ Status 200 |
| 2 | `test_api_prediction_endpoint` | AI prediction works | ✅ Returns risk_score |
| 3 | `test_api_response_time_under_200ms` | API latency < 200ms | ✅ Response < 200ms |

---

## 🔴 Negative Test Scenarios (Should Fail/Catch Errors)

### Synthea Dataset

| # | Test Name | What We Test | Expected Result |
|---|-----------|--------------|-----------------|
| 1 | `test_synthea_invalid_heart_rate_detected` | Heart rate = 250 bpm (impossible) | ❌ Detected as invalid (>180) |
| 2 | `test_synthea_missing_patient_id` | Patient ID is null | ❌ Missing ID detected |
| 3 | `test_synthea_invalid_gender_value` | Gender = "X" (invalid) | ❌ Invalid gender caught |
| 4 | `test_synthea_future_birthdate` | Birth date = 2030 (future) | ❌ Future date detected |
| 5 | `test_synthea_empty_dataframe_rejected` | Empty dataframe | ❌ Empty data rejected |

### FHIR Dataset

| # | Test Name | What We Test | Expected Result |
|---|-----------|--------------|-----------------|
| 1 | `test_fhir_invalid_resource_type` | resourceType = "InvalidType" | ❌ Invalid type detected |
| 2 | `test_fhir_missing_required_field` | Missing resourceType field | ❌ Missing field caught |
| 3 | `test_fhir_invalid_gender_value` | Invalid gender value | ❌ Validation fails |
| 4 | `test_fhir_empty_bundle` | Empty entry array | ❌ Empty bundle detected |
| 5 | `test_fhir_invalid_json_structure` | Malformed JSON | ❌ JSON decode error |

### NIH Chest X-ray Dataset

| # | Test Name | What We Test | Expected Result |
|---|-----------|--------------|-----------------|
| 1 | `test_nih_missing_metadata_file` | Metadata file missing | ❌ Handled gracefully |
| 2 | `test_nih_invalid_image_path` | Non-existent image path | ❌ Path doesn't exist |
| 3 | `test_nih_missing_disease_label` | Missing disease column | ❌ Column not found |
| 4 | `test_nih_duplicate_image_index` | Duplicate image IDs | ❌ Duplicates detected |
| 5 | `test_nih_invalid_disease_value` | Disease value = 2 (should be 0/1) | ❌ Invalid value caught |

---

## 🚀 How to Run Tests

### Option 1: Run All Tests
```bash
# Mac/Linux
chmod +x run_tests.sh
./run_tests.sh

# Windows
run_tests.bat