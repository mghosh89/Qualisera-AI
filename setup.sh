#!/bin/bash

echo "🏥 Qualisera- AI - Complete Setup Script"
echo "======================================"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

echo "✓ Python found: $(python3 --version)"

# Create virtual environment
echo "\n📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "\n📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create directory structure
echo "\n Creating directory structure..."
mkdir -p data/{synthea,nih_cxr,fhir}
mkdir -p reports output logs

# Download Synthea JAR
echo "\n⬇️  Downloading Synthea..."
if [ ! -f "synthea-with-dependencies.jar" ]; then
    curl -L -o synthea-with-dependencies.jar \
    https://github.com/synthetichealth/synthea/releases/download/master-branch-latest/synthea-with-dependencies.jar
    echo "✓ Synthea downloaded"
else
    echo "✓ Synthea already exists"
fi

# Generate sample Synthea data
echo "\n Generating 1000 synthetic patients..."
java -jar synthea-with-dependencies.jar -p 1000 \
    --exporter.csv.export true \
    --exporter.fhir.export true

# Move generated files
if [ -d "output" ]; then
    mv output/csv/* data/synthea/ 2>/dev/null || true
    mv output/fhir/* data/fhir/ 2>/dev/null || true
    echo "✓ Synthetic data generated and moved to data/synthea/"
fi

# Create .env file
echo "\n🔐 Creating .env file..."
cat > .env << EOF
# Qualisera AI Environment Variables

# FHIR Server
FHIR_SERVER=https://hapi.fhir.org/baseR4

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5000
EOF

echo "\n✅ Setup complete!"
echo "\n======================================"
echo "Next steps:"
echo "1. Activate environment: source venv/bin/activate"
echo "2. Edit .env file with your credentials"
echo "3. Run: python run_qualisera.py --dataset synthea --validate"
echo "======================================\n"