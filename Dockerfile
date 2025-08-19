FROM selenium/standalone-chromium:latest

# Switch to root (to copy files)
USER root

# Set working directory
WORKDIR /app

# Copy your source code
COPY . .

# Install dependencies (pip is already in /opt/venv)
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Run the scraper
CMD ["python", "main.py"]
