"""
Qualisera AI - Synthetic Data Loader
Loads and prepares Synthea-generated data for QA validation
"""
import pandas as pd
from pathlib import Path

class SyntheticDataLoader:
    """Loads synthetic healthcare data from Synthea CSV exports."""
    
    def __init__(self, data_dir: str | Path | None = None):
        self.data_dir = (
            Path(data_dir)
            if data_dir is not None
            else Path(__file__).resolve().parents[2] / "data" / "synthetic"
        )
        
    def load_patients(self) -> pd.DataFrame:
        """Load patient demographics."""
        file_path = self.data_dir / "patients.csv"
        if not file_path.exists():
            raise FileNotFoundError(f"Patient data not found at {file_path}")
        return pd.read_csv(file_path)
    
    def load_observations(self) -> pd.DataFrame:
        """Load patient vitals (heart rate, BP, etc.)."""
        file_path = self.data_dir / "observations.csv"
        if not file_path.exists():
            raise FileNotFoundError(f"Observations not found at {file_path}")
        return pd.read_csv(file_path)
    
    def load_conditions(self) -> pd.DataFrame:
        """Load patient diagnoses."""
        file_path = self.data_dir / "conditions.csv"
        return pd.read_csv(file_path) if file_path.exists() else pd.DataFrame()
    
    def get_summary_stats(self) -> dict:
        """Generate summary statistics for QA reporting."""
        patients = self.load_patients()
        observations = self.load_observations()
        
        return {
            "total_patients": len(patients),
            "total_observations": len(observations),
            "date_range": {
                "start": observations["DATE"].min() if not observations.empty else None,
                "end": observations["DATE"].max() if not observations.empty else None
            }
        }

if __name__ == "__main__":
    loader = SyntheticDataLoader()
    stats = loader.get_summary_stats()
    print("📊 Qualisera AI - Data Summary:")
    print(f"   Patients loaded: {stats['total_patients']}")
    print(f"   Observations loaded: {stats['total_observations']}")