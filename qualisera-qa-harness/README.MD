# Qualisera QA Harness

Synthetic-first pre-deployment validation for clinical AI workflows.
A quality-assurance harness that loads synthetic/FHIR/NIH test data,
exercises a mock inference API, and renders a test dashboard.

> ⚠️ This repository contains the **open architecture** (loaders, mock API,
> reporting, orchestration gate). The concrete clinical-plausibility
> validation rules are proprietary and provided via `qualisera-core`.

## 📖 Cite this work
Ghosh, M. (2026). A Synthetic-First Quality Assurance Pipeline for
Pre-Deployment Clinical AI Validation. Zenodo.
https://doi.org/10.5281/zenodo.24312873
USPTO Provisional App. No. 64/203,372 (filed Nov 20, 2026).

## 🏗️ Architecture (see Fig. 1 of the paper)
loaders → [validators] → mock API → JUnit → dashboard
                ↑
        orchestration gate (route / quarantine / reject)

## 🚀 Quick start
pip install -r requirements.txt
pytest -q
python -m harness.reporting.dashboard

## 🔐 What's public vs private
| Component        | Public? | Notes                          |
|------------------|---------|--------------------------------|
| Loaders          | ✅      | thin I/O interfaces            |
| Mock API         | ✅      | deterministic rule-based mock  |
| Dashboard        | ✅      | reporting only                 |
| Orchestration gate| ✅     | the --validate controller      |
| Validation rules | 🔒      | proprietary (qualisera-core)   |

## 🤝 Related
Built on top of [Synthea](https://github.com/synthetichealth/synthea)
data. See my contribution to MITRE's
[chatty-notes](https://github.com/synthetichealth/chatty-notes/pull/3).