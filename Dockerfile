FROM python:3.9-slim-bullseye
WORKDIR /chatbot

# Install Java + build dependencies for pyserini
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openjdk-11-jre \
    ca-certificates-java \
    build-essential \
    gcc \
    g++ \
    && \
    apt-get clean && \
    update-ca-certificates -f && \
    rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64/

# Upgrade pip first
RUN pip install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /chatbot

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PORT=5000

EXPOSE 5000

# Use gunicorn for production with increased timeout for model inference
CMD gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 1 app:app