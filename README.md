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