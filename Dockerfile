# Use a lightweight Python image
FROM python:3.11-slim

# Install system dependencies for Tesseract
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tesseract-ocr \
        libtesseract-dev && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory for the project
WORKDIR /app

# Copy all repo files into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Move into the Datathon folder where app.py lives
WORKDIR /app/Datathon

# Expose the port Render will hit (not strictly required)
EXPOSE 8000

# Start FastAPI using Uvicorn
# Render automatically injects the PORT environment variable
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
