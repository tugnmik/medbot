# Use Python 3.9 slim image
FROM python:3.9-slim-bullseye

WORKDIR /chatbot

# Install Java for VnCoreNLP + build tools + Rust for tiktoken
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openjdk-11-jre-headless \
    build-essential \
    curl \
    && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64/
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy and install requirements
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

COPY . /chatbot

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PORT=5000

EXPOSE 5000

# Use gunicorn for production
CMD gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 1 app:app