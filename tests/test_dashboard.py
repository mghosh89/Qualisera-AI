from pathlib import Path

from scripts.generate_test_dashboard import _read_results, render_dashboard


def test_dashboard_renders_suite_totals_and_positive_negative_scenarios(tmp_path):
    results_file = tmp_path / "results.xml"
    results_file.write_text(
        """<testsuites><testsuite>
        <testcase classname="tests.test_all_datasets.TestSyntheaPositive"
                  name="test_patients_csv_loads_successfully" time="0.2" />
        <testcase classname="tests.test_all_datasets.TestSyntheaNegative"
                  name="test_rejects_future_birthdate" time="0.1">
          <failure message="Invalid date">Invalid date</failure>
        </testcase>
        <testcase classname="tests.test_clinical_data_scenarios.TestFHIRPositive"
                  name="test_accepts_gender[male]" time="0.1" />
        <testcase classname="tests.test_api.TestAPIHealth"
                  name="test_health_endpoint" time="0.05">
          <skipped message="API unavailable" />
        </testcase>
        </testsuite></testsuites>"""
    )

    dashboard = render_dashboard(_read_results(results_file))

    assert "Tests collected" in dashboard
    assert "Results by test suite" in dashboard
    assert "Dataset positive scenarios" in dashboard
    assert "Dataset negative scenarios" in dashboard
    assert "Dataset scenarios" in dashboard
    assert "3 dataset scenarios across Synthea, FHIR, and NIH" in dashboard
    assert "API scenarios (separate)" in dashboard
    assert "Patients CSV loads successfully" in dashboard
    assert "Male" in dashboard
    assert "Rejects future birthdate" in dashboard
    assert "Synthea Negative" in dashboard
    assert "Failed" in dashboard
    assert "Skipped" in dashboard
