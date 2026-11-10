#!/bin/bash

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

python -m pytest tests/ -v --tb=short --color=yes