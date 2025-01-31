# Use the official lightweight Python base image
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first (to leverage Docker caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application to the working directory
COPY . .

# Expose Streamlit's default port
EXPOSE 8501

# Add healthcheck (optional, but good for production)
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run the Streamlit application
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]