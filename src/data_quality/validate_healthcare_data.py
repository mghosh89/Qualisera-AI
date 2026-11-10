"""
Qualisera AI - Healthcare Data Quality Validation
Validates synthetic patient data against clinical safety rules.
"""
from datetime import date

import pandas as pd
from data_loader import SyntheticDataLoader

class HealthcareDataValidator:
    """Validates healthcare data for clinical safety and schema compliance."""
    
    def __init__(self):
        self.loader = SyntheticDataLoader()
    
    def validate_patient_data(self) -> dict:
        """Validate patient demographics against clinical rules."""
        df = self.loader.load_patients()
        expectations = []

        def add_expectation(expectation_type: str, success: bool, **result) -> None:
            expectations.append({
                "success": bool(success),
                "expectation_type": expectation_type,
                "result": result,
            })

        has_id = "Id" in df.columns
        add_expectation("expect_column_to_exist", has_id, column="Id")
        add_expectation(
            "expect_column_values_to_not_be_null",
            has_id and df["Id"].notna().all(),
            column="Id",
        )

        has_birthdate = "BIRTHDATE" in df.columns
        birthdates = (
            pd.to_datetime(df["BIRTHDATE"], errors="coerce")
            if has_birthdate
            else pd.Series(dtype="datetime64[ns]")
        )
        valid_birthdates = birthdates.between(
            pd.Timestamp("1900-01-01"), pd.Timestamp(date.today())
        )
        add_expectation(
            "expect_column_values_to_be_between",
            has_birthdate and valid_birthdates.mean() >= 0.99,
            column="BIRTHDATE",
            min_value="1900-01-01",
            max_value=date.today().isoformat(),
            unexpected_count=int((~valid_birthdates).sum()),
        )

        has_gender = "GENDER" in df.columns
        add_expectation(
            "expect_column_values_to_not_be_null",
            has_gender and df["GENDER"].notna().all(),
            column="GENDER",
        )
        valid_genders = (
            df["GENDER"].isin(["M", "F", "Other"])
            if has_gender
            else pd.Series(False, index=df.index)
        )
        add_expectation(
            "expect_column_values_to_be_in_set",
            has_gender and valid_genders.all(),
            column="GENDER",
            value_set=["M", "F", "Other"],
            unexpected_count=int((~valid_genders).sum()),
        )

        successful_expectations = sum(r["success"] for r in expectations)
        success = successful_expectations == len(expectations)
        return {
            "success": success,
            "statistics": {
                "evaluated_expectations": len(expectations),
                "successful_expectations": successful_expectations,
                "unsuccessful_expectations": len(expectations) - successful_expectations,
                "success_percent": successful_expectations / len(expectations) * 100,
            },
            "failed_expectations": [r for r in expectations if not r["success"]],
        }
    
    def validate_vitals_data(self) -> dict:
        """Validate patient vitals against medical safety ranges."""
        df = self.loader.load_observations()
        
        # Filter for specific vital signs
        heart_rate = df[df["DESCRIPTION"].str.contains("Heart rate", case=False, na=False)]
        
        if not heart_rate.empty:
            values = pd.to_numeric(heart_rate["VALUE"], errors="coerce")
            in_range = values.between(40, 180)
            successful_expectations = int(in_range.sum())
            success_percent = successful_expectations / len(heart_rate) * 100
            success = success_percent >= 95
            return {
                "metric": "heart_rate",
                "success": success,
                "statistics": {
                    "evaluated_expectations": 1,
                    "successful_expectations": int(success),
                    "unsuccessful_expectations": int(not success),
                    "success_percent": success_percent,
                    "evaluated_values": len(heart_rate),
                    "values_in_range": successful_expectations,
                    "values_out_of_range": int((~in_range).sum()),
                },
            }
        return {"metric": "heart_rate", "success": True, "message": "No data"}

if __name__ == "__main__":
    validator = HealthcareDataValidator()
    
    print("🔍 Validating patient demographics...")
    patient_results = validator.validate_patient_data()
    print(f"   ✅ Success: {patient_results['success']}")
    
    print("\n🔍 Validating vital signs...")
    vitals_results = validator.validate_vitals_data()
    print(f"   ✅ Success: {vitals_results['success']}")