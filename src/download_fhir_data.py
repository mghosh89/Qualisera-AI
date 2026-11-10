"""
Simple FHIR Data Downloader
Downloads sample FHIR resources from HAPI test server
"""
import requests
import json
from pathlib import Path

# HAPI FHIR Test Server
FHIR_SERVER = "https://hapi.fhir.org/baseR4"

def download_fhir_data(resource_type: str, count: int = 100):
    """Download FHIR resources from HAPI server"""
    print(f"📥 Downloading {count} {resource_type} resources from HAPI FHIR...")

    try:
        # Make request to FHIR server
        url = f"{FHIR_SERVER}/{resource_type}?_count={count}"
        headers = {"Accept": "application/fhir+json"}

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 200:
            bundle = response.json()

            # Create output directory
            output_dir = Path("data/fhir")
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save the bundle
            output_file = output_dir / f"{resource_type.lower()}_bundle.json"
            with open(output_file, 'w') as f:
                json.dump(bundle, f, indent=2)

            # Count entries
            entries = bundle.get("entry", [])
            print(f"✅ Successfully downloaded {len(entries)} {resource_type} resources")
            print(f"📁 Saved to: {output_file}")

            return bundle
        else:
            print(f"❌ Error: Server returned status {response.status_code}")
            return None

    except requests.exceptions.Timeout:
        print("❌ Error: Request timed out. The HAPI server might be slow.")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to HAPI FHIR server. Check your internet connection.")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    """Download sample FHIR resources"""
    print("="*60)
    print(" Qualisera AI - FHIR Data Downloader")
    print("="*60)

    # Download Patients
    print("\n1️⃣  Downloading Patient resources...")
    patients = download_fhir_data("Patient", count=50)

    # Download Observations (if patients were successful)
    if patients:
        print("\n2️⃣  Downloading Observation resources...")
        observations = download_fhir_data("Observation", count=100)

        print("\n3️⃣  Downloading Condition resources...")
        conditions = download_fhir_data("Condition", count=50)

    print("\n" + "="*60)
    print("✅ FHIR data download complete!")
    print("="*60)
    print("\nNext step: python run_qualisera.py --dataset fhir")


if __name__ == "__main__":
    main()