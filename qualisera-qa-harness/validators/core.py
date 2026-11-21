# validators/core.py  (PUBLIC repo)
"""Synthetic-first validation interface.

The concrete clinical-plausibility rules (identifier uniqueness,
birth-date historical bounds, the 40-180 heart-rate screen, FHIR
resource/label checks) are implemented in the private core package
and are not redistributed here. See the working paper for the
methodology: DOI 10.5281/zenodo.24312873
"""

class SyntheaValidator:
    def validate_patients(self, df):
        raise NotImplementedError(
            "Core validation logic is proprietary. "
            "Install `qualisera-core` for the reference implementation."
        )

    def screen_heart_rate(self, df, lo=40, hi=180, tol=0.05):
        raise NotImplementedError(...)