# Use an official Python slim image (Debian-based)
FROM python:3.11-slim

# Install Chromium browser and matching ChromeDriver via apt
# (chromium-driver is always version-matched with chromium in Debian repos)
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy and install Python dependencies first (leverages Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source code
COPY . .

# Default command: run the scraper
CMD ["python", "main.py"]
