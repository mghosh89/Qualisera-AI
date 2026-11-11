#!/bin/bash

project_root="$(cd "$(dirname "$0")" && pwd)"
cd "$project_root"

echo "🏥 Qualisera AI - Comprehensive Test Suite"
echo "=========================================="
echo ""

# Activate the project virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Run: python -m venv .venv"
    exit 1
fi

echo ""
echo "🧪 Running Test Suite..."
echo ""

mkdir -p reports
junit_file="$(mktemp "${TMPDIR:-/tmp}/qualisera-junit.XXXXXX")"
trap 'rm -f "$junit_file"' EXIT

set +e
python -m pytest tests/ -v --tb=short --color=yes --junitxml="$junit_file"
test_status=$?
set -e

python scripts/generate_test_dashboard.py "$junit_file" reports/test_report.html
exit "$test_status"