"""
Qualisera AI - Main Orchestrator Script
Supports multiple healthcare data sources
"""
import os
import argparse
from pathlib import Path
from src.data_ingestion import DataFactory


def setup_environment():
    """Setup environment variables and directories"""
    print("="*60)
    print(" Qualisera AI: Multi-Source Healthcare MLOps QA Framework")
    print("="*60)

    # Create necessary directories
    directories = [
        "data/synthea",
        "data/nih_cxr",
        "data/fhir",
        "reports",
        "output"
    ]

    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {dir_path}")


def load_dataset(dataset_type: str, config: dict = None):
    """
    Load dataset using appropriate loader

    Args:
        dataset_type: Type of dataset (synthea, nih, fhir)
        config: Configuration dictionary
    """
    print(f"\n📊 Loading {dataset_type.upper()} dataset...")

    try:
        loader = DataFactory.get_loader(dataset_type, config)
        summary = loader.get_summary()

        print("\n" + "="*60)
        print(f"Dataset: {summary.get('dataset_type')}")
        print("="*60)
        for key, value in summary.items():
            print(f"{key}: {value}")

        return loader
    except Exception as e:
        print(f"❌ Error loading {dataset_type} dataset: {e}")
        return None


def run_data_quality_checks(loader, dataset_type: str):
    """Run data quality validation"""
    print(f"\n🔍 Running data quality checks for {dataset_type}...")

    # Import validation module
    from src.data_quality.validate_healthcare_data import HealthcareDataValidator

    validator = HealthcareDataValidator(data_dir=loader.data_dir)

    if dataset_type == "synthea":
        results = validator.validate_patient_data()
        print(f"✓ Validation Results: {results['success']}")
        if not results["success"]:
            print(f"  Failed checks: {results['failed_expectations']}")

    print("✓ Data quality checks completed")


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Qualisera AI - Multi-Source Healthcare MLOps QA"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="synthea",
        choices=["synthea", "nih", "fhir", "all"],
        help="Dataset to load (default: synthea)"
    )
    parser.add_argument(
        "--patient-count",
        type=int,
        default=1000,
        help="Number of patients to generate (for Synthea)"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run data quality validation"
    )

    args = parser.parse_args()

    # Setup environment
    setup_environment()

    # List available datasets
    if args.dataset == "all":
        print("\n📚 Supported Datasets:")
        for ds in DataFactory.list_supported_datasets():
            print(f"  - {ds}")
        print("\nUse --dataset <name> to load a specific dataset")
        return

    # Configuration
    config = {
        "data_dir": {
            "synthea": "data/synthea",
            "nih": "data/nih_cxr",
            "fhir": "data/fhir",
        }[args.dataset],
        "patient_count": args.patient_count,
        "fhir_server": os.getenv("FHIR_SERVER", "https://hapi.fhir.org/baseR4")
    }

    # Load dataset
    loader = load_dataset(args.dataset, config)

    if not loader:
        print("\n❌ Failed to load dataset. Exiting.")
        return

    # Run validation if requested
    if args.validate:
        run_data_quality_checks(loader, args.dataset)

    print("\n" + "="*60)
    print("✅ Setup complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Review the loaded data in the data/ directory")
    print("2. Run: python run_qualisera.py --dataset <type> --validate")
    print("3. Start API: uvicorn src.api.mock_ai_service:app --reload")


if __name__ == "__main__":
    main()