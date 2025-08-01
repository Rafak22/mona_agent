# Use an official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependencies and setup files
COPY requirements.txt .
COPY setup.py .
COPY pyproject.toml .

# Install dependencies and the package in development mode
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e .

# Copy the rest of your app
COPY . .

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]