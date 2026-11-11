"""
Qualisera AI - Healthcare Data Quality Validation
Validates synthetic patient data against clinical safety rules.
"""
from datetime import date

import pandas as pd
from .data_loader import SyntheticDataLoader

class HealthcareDataValidator:
    """Validates healthcare data for clinical safety and schema compliance."""
    
    def __init__(self, data_dir=None):
        self.loader = SyntheticDataLoader(data_dir)
    
    def validate_patient_data(self) -> dict:
        """Validate patient demographics against clinical rules."""
        return self.validate_patient_dataframe(self.loader.load_patients())

    def validate_patient_dataframe(self, df: pd.DataFrame) -> dict:
        """Validate a patient DataFrame against clinical rules."""
        expectations = []

        def add_expectation(expectation_type: str, success: bool, **result) -> None:
            expectations.append({
                "success": bool(success),
                "expectation_type": expectation_type,
                "result": result,
            })

        add_expectation(
            "expect_table_row_count_to_be_between",
            not df.empty,
            min_value=1,
        )

        has_id = "Id" in df.columns
        add_expectation("expect_column_to_exist", has_id, column="Id")
        add_expectation(
            "expect_column_values_to_not_be_null",
            has_id and df["Id"].notna().all(),
            column="Id",
        )
        nonblank_ids = (
            df["Id"].map(lambda value: bool(str(value).strip()))
            if has_id
            else pd.Series(False, index=df.index)
        )
        add_expectation(
            "expect_column_values_to_not_be_blank",
            has_id and nonblank_ids.all(),
            column="Id",
        )
        unique_ids = has_id and not df["Id"].duplicated().any()
        add_expectation(
            "expect_column_values_to_be_unique",
            unique_ids,
            column="Id",
            duplicate_count=(
                int(df["Id"].duplicated().sum()) if has_id else 0
            ),
        )

        has_birthdate = "BIRTHDATE" in df.columns
        def is_valid_birthdate(value) -> bool:
            try:
                birthdate = date.fromisoformat(str(value))
            except ValueError:
                return False
            return date(1900, 1, 1) <= birthdate <= date.today()

        valid_birthdates = (
            df["BIRTHDATE"].map(is_valid_birthdate)
            if has_birthdate
            else pd.Series(False, index=df.index)
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

        if "DEATHDATE" in df.columns:
            has_valid_deathdate = df.apply(
                lambda row: self._is_valid_deathdate(
                    row.get("DEATHDATE"), row.get("BIRTHDATE")
                ),
                axis=1,
            )
            add_expectation(
                "expect_deathdate_to_follow_birthdate",
                has_valid_deathdate.all(),
                unexpected_count=int((~has_valid_deathdate).sum()),
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

    @staticmethod
    def _is_valid_deathdate(deathdate, birthdate) -> bool:
        if pd.isna(deathdate) or str(deathdate).strip() == "":
            return True
        try:
            parsed_deathdate = date.fromisoformat(str(deathdate))
            parsed_birthdate = date.fromisoformat(str(birthdate))
        except (TypeError, ValueError):
            return False
        return parsed_birthdate <= parsed_deathdate <= date.today()
    
    def validate_vitals_data(self) -> dict:
        """Validate patient vitals against medical safety ranges."""
        return self.validate_vitals_dataframe(self.loader.load_observations())

    def validate_vitals_dataframe(self, df: pd.DataFrame) -> dict:
        """Validate heart-rate observations in a DataFrame."""
        required_columns = {"DESCRIPTION", "VALUE"}
        if not required_columns.issubset(df.columns):
            return {
                "metric": "heart_rate",
                "success": False,
                "message": f"Missing required columns: {sorted(required_columns - set(df.columns))}",
            }

        if df.empty:
            return {
                "metric": "heart_rate",
                "success": False,
                "message": "No observations to validate",
            }

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
        return {"metric": "heart_rate", "success": False, "message": "No heart-rate data"}

if __name__ == "__main__":
    validator = HealthcareDataValidator()
    
    print("🔍 Validating patient demographics...")
    patient_results = validator.validate_patient_data()
    print(f"   ✅ Success: {patient_results['success']}")
    
    print("\n🔍 Validating vital signs...")
    vitals_results = validator.validate_vitals_data()
    print(f"   ✅ Success: {vitals_results['success']}")