"""Synthetic-first validation interface (QualiseraAI).

The concrete clinical-plausibility rules — identifier uniqueness,
the 99% birth-date historical-bound threshold, the 40-180 bpm
heart-rate screen with 95% tolerance, and the FHIR/NIH resource
checks described in §5.3 of the working paper — are implemented in
the PRIVATE core package and are not redistributed here.

Methodology (public, DOI-stamped):
    Ghosh, M. (2026). A Synthetic-First Quality Assurance Pipeline
    for Pre-Deployment Clinical AI Validation. Zenodo.
    https://doi.org/10.5281/zenodo.24312873
    USPTO Provisional App. No. 64/203,372 (filed 2026-11-20).
"""


class SyntheaValidator:
    """Patient table + heart-rate screening (see §5.3)."""

    def validate_patients(self, df):
        raise NotImplementedError(
            "Core patient validation (id uniqueness, birth-date 99% "
            "threshold, gender set) is proprietary. Install "
            "`qualisera-core` for the reference implementation."
        )

    def screen_heart_rate(self, df, lo=40, hi=180, tol=0.05):
        raise NotImplementedError(
            "Core heart-rate screen (40-180, 95% tolerance) is "
            "proprietary. See §5.3 of the working paper."
        )


class FhirValidator:
    def validate_bundle(self, bundle):
        raise NotImplementedError("See §5.2-5.3; private core.")


class NihValidator:
    def validate_metadata(self, df):
        raise NotImplementedError("See §5.2-5.3; private core.")