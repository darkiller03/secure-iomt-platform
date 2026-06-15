FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /app

# Default command runs the FastAPI service
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
