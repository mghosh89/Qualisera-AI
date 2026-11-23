# QualiseraAI — Synthetic-First Pre-Deployment Validation

QA harness for clinical AI workflows: load synthetic/FHIR/NIH test
data → validate → exercise a mock inference API → render a dashboard.

> ⚠️ This repo is the **open architecture** (loaders, mock API,
> reporting, orchestration gate). The concrete clinical-plausibility
> rules (§5.3) are proprietary and provided via `qualisera-core`.

## 📖 Cite
Ghosh, M. (2026). A Synthetic-First Quality Assurance Pipeline for
Pre-Deployment Clinical AI Validation. Zenodo.
https://doi.org/10.5281/zenodo.24312873
USPTO Provisional App. No. 64/203,372 (filed 2026-11-20).

## 🏗️ Flow (§5.6)
loaders → [validators 🔒] → mock API → JUnit → dashboard
                  ↑
        orchestration gate (route / quarantine / reject)

## 🔐 Public vs private
| Component | Public | Patent § |
|---|---|---|
| Loaders | ✅ | 5.2 |
| Mock API | ✅ | 5.4 |
| Dashboard | ✅ | 5.5 |
| Gate | ✅ | 5.6 |
| Validation rules | 🔒 | 5.3 |

## 🤝 Related
Built atop [Synthea](https://github.com/synthetichealth/synthea).
See my MITRE contribution:
[chatty-notes PR #3](https://github.com/synthetichealth/chatty-notes/pull/3).

## 🚀 Run
pip install -r requirements.txt && pytest -q

## 🛠️ Implementation Note
This repository was developed using AI-assisted coding tools (GitHub Copilot) for syntax generation and boilerplate code. **All architecture, validation logic, patent claims, and clinical plausibility rules are the original work of the inventor (Moumita Ghosh).**