FROM selenium/standalone-chromium:latest

# Use root so we can install Python
USER root

# Install Python and pip (no distutils needed in Ubuntu 24.04)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
 && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy your source code
COPY . .

# Install dependencies
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Run the scraper
CMD ["python3", "main.py"]
