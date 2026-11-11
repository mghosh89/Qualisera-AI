> **Proprietary software.** All rights are reserved; no rights to use, copy, modify, or
> distribute the project are granted without written authorization. See
> [PROPRIETARY.md](./PROPRIETARY.md). Third-party software, standards, and data
> remain subject to their respective terms. No patent filing or grant is
> represented.

## 📚 Supported Datasets

Qualisera AI supports multiple healthcare data sources for comprehensive testing:

### 1. **Synthea™** (Recommended for Testing)
- **Type**: Synthetic patient population
- **Access**: Free, no credentials required
- **Format**: CSV, FHIR JSON
- **Setup**: Automatic (included in setup script)

### 2. **NIH Chest X-ray** (Medical Imaging)
- **Type**: Chest X-ray images with disease labels
- **Access**: Free download
- **Format**: PNG images + CSV metadata
- **Setup**: Download from [NIH](https://nihcc.app.box.com/v/ChestXray-NIHCC) or Kaggle

### 3. **FHIR Test Data** (Standard Healthcare API)
- **Type**: HL7 FHIR standard resources
- **Access**: Public FHIR servers
- **Format**: FHIR JSON
- **Setup**: Automatic from public servers

## 🚀 Quick Start with Different Datasets

### Using Synthea (Default)
```bash
python run_qualisera.py --dataset synthea --patient-count 1000 --validate
```

## Run tests and view the dashboard

```bash
./run_tests.sh
```

The script runs the complete test suite and refreshes the results dashboard at
[`reports/test_report.html`](./reports/test_report.html). Scenario names and
positive/negative outcomes are documented in
[`docs/Test_Scenarios.md`](./docs/Test_Scenarios.md).