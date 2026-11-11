"""
NIH Chest X-ray Dataset Loader
Loads NIH Clinical Center Chest X-ray Dataset
"""
import pandas as pd
from pathlib import Path
from typing import Dict, Any


class NIHDataLoader:
    """Loader for NIH Chest X-ray dataset"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data_dir = Path(config.get("data_dir", "data/nih_cxr")).expanduser()
        if not self.data_dir.is_absolute():
            project_root = Path(__file__).resolve().parents[2]
            self.data_dir = project_root / self.data_dir
        self.dataset_url = "https://nihcc.app.box.com/v/ChestXray-NIHCC"

    def _metadata_file(self) -> Path | None:
        candidates = (
            self.data_dir / "Data_Entry_2017.csv",
            self.data_dir / "Data_Entry_2017_v2020.csv",
        )
        return next(
            (path for path in candidates if path.is_file()),
            next(iter(sorted(self.data_dir.glob("Data_Entry_2017*.csv"))), None),
        )

    def download_metadata(self) -> pd.DataFrame:
        """Download dataset metadata (Data_Entry_2017.csv)"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        metadata_file = self._metadata_file()

        if metadata_file is not None:
            print("✓ NIH metadata found")
            return pd.read_csv(metadata_file)

        print("NIH Chest X-ray metadata not found.")
        print(f"Please download from: {self.dataset_url}")
        print("Or use Kaggle: kaggle datasets download -d nih-chest-xrays/data")

        return pd.DataFrame()

    def load_image_paths(self) -> pd.DataFrame:
        """Load image file paths and labels"""
        metadata = self.download_metadata()
        if metadata.empty:
            return pd.DataFrame()

        images_dir = self.data_dir / "images"
        image_paths = metadata["Image Index"].map(
            lambda filename: next(
                (
                    path
                    for path in (images_dir / filename, self.data_dir / filename)
                    if path.is_file()
                ),
                images_dir / filename,
            )
        )
        metadata = metadata.copy()
        metadata.loc[:, "full_path"] = image_paths

        return metadata

    def validate_metadata(self, metadata: pd.DataFrame) -> dict[str, Any]:
        """Check NIH metadata schema, image identifiers, and finding labels."""
        errors = []
        required_columns = {"Image Index", "Finding Labels"}
        missing_columns = required_columns - set(metadata.columns)
        if missing_columns:
            errors.append(f"Missing required columns: {sorted(missing_columns)}")
            return {"success": False, "errors": errors}
        if metadata.empty:
            errors.append("Metadata contains no records")
        if metadata["Image Index"].isna().any():
            errors.append("Image Index contains null values")
        if metadata["Image Index"].map(
            lambda value: isinstance(value, str) and not value.strip()
        ).any():
            errors.append("Image Index contains blank values")
        if metadata["Image Index"].map(
            lambda value: isinstance(value, str)
            and (
                Path(value).name != value
                or "/" in value
                or "\\" in value
            )
        ).any():
            errors.append("Image Index contains an invalid path")
        if metadata["Image Index"].duplicated().any():
            errors.append("Image Index contains duplicate values")

        valid_labels = {
            "Atelectasis",
            "Cardiomegaly",
            "Effusion",
            "Infiltration",
            "Mass",
            "Nodule",
            "Pneumonia",
            "Pneumothorax",
            "Consolidation",
            "Edema",
            "Emphysema",
            "Fibrosis",
            "Pleural_Thickening",
            "Hernia",
            "No Finding",
        }
        for value in metadata["Finding Labels"].dropna():
            labels = str(value).split("|")
            if not labels or any(label not in valid_labels for label in labels):
                errors.append("Finding Labels contains an unsupported label")
                break
        if metadata["Finding Labels"].isna().any():
            errors.append("Finding Labels contains null values")
        if metadata["Finding Labels"].map(
            lambda value: isinstance(value, str) and not value.strip()
        ).any():
            errors.append("Finding Labels contains blank values")
        if metadata["Finding Labels"].map(
            lambda value: isinstance(value, str)
            and "No Finding" in value.split("|")
            and len(value.split("|")) > 1
        ).any():
            errors.append("No Finding cannot be combined with another label")

        optional_checks = {
            "Patient Age": lambda values: pd.to_numeric(
                values, errors="coerce"
            ).between(0, 120),
            "Patient Gender": lambda values: values.isin(["M", "F"]),
            "View Position": lambda values: values.isin(["AP", "PA"]),
        }
        for column, check in optional_checks.items():
            if column in metadata.columns and not check(metadata[column]).all():
                errors.append(f"{column} contains invalid values")

        return {"success": not errors, "errors": errors}

    def get_disease_statistics(self) -> pd.DataFrame:
        """Get statistics of disease labels"""
        metadata = self.load_image_paths()
        if metadata.empty:
            return pd.DataFrame()

        if "Finding Labels" not in metadata.columns:
            raise ValueError("NIH metadata is missing the 'Finding Labels' column")

        labels = metadata["Finding Labels"].fillna("").str.split("|").explode()
        labels = labels[labels.ne("")]
        counts = labels.value_counts()
        stats = {
            label: {
                "count": int(count),
                "percentage": float(count / len(metadata) * 100),
            }
            for label, count in counts.items()
        }
        return pd.DataFrame(stats)

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of NIH dataset"""
        metadata = self.load_image_paths()

        return {
            "dataset_type": "NIH Chest X-ray",
            "total_images": len(metadata),
            "available_images": (
                int(metadata["full_path"].map(Path.is_file).sum())
                if not metadata.empty
                else 0
            ),
            "data_directory": str(self.data_dir),
            "note": "Metadata records may reference images not downloaded locally"
        }