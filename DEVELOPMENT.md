# Internal Development Guide

Qualisera AI is proprietary software. Development access is limited to people
authorized by the rights holder. This document is an internal workflow guide,
not an invitation to fork, contribute, or redistribute the project.

## Engineering workflow

- Keep changes focused and review them before merging.
- Add or update automated tests for behavior changes.
- Run the relevant tests before integrating changes:

  ```bash
  ./run_tests.sh
  ```

- Update related documentation when behavior or setup instructions change.
- Do not add real patient information, credentials, or confidential third-party
  materials to source control. Use synthetic or properly authorized test data.
- Verify that dependencies and datasets are used in accordance with their
  respective licenses and terms.

## Intellectual-property handling

- Limit access to authorized collaborators and use approved private storage.
- Do not publish implementation details, screenshots, code, or technical
  descriptions externally without written authorization.
- Record the date, authors, and technical details of potentially novel work in
  approved internal records.
- Consult qualified intellectual-property counsel before making patent,
  ownership, confidentiality, or public-disclosure decisions.