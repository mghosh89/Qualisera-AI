# Qualisera AI - Production Docker Image
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY docker/requirements.txt .
RUN python -m pip install --no-cache-dir --requirement=requirements.txt

# Copy application code
COPY src/ ./src/
COPY tests/ ./tests/

# Expose API port
EXPOSE 8000

# Run the API
CMD ["uvicorn", "src.api.mock_ai_service:app", "--host", "0.0.0.0", "--port", "8000"]