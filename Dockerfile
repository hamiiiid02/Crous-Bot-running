FROM debian:bullseye

# Install Chromium and dependencies (but NOT chromedriver!)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-distutils \
    wget \
    unzip \
    curl \
    gnupg \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxss1 \
    libappindicator1 \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    chromium \
 && rm -rf /var/lib/apt/lists/*

# Set environment variable so Selenium knows where Chromium is
ENV CHROME_BIN=/usr/bin/chromium
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy all source files into the image
COPY . .

# Install Python packages
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Run the app
CMD ["python3", "main.py"]
